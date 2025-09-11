"""Cache middleware for automatic response caching"""

import json
import time
from typing import Callable, Optional, Set
from datetime import timedelta

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.cache import cache, cache_key, CacheError, CircuitBreakerError
from app.utils.structured_logger import get_logger

logger = get_logger("cache_middleware")

class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic HTTP response caching.
    
    Caches GET requests for specified routes with configurable TTL.
    """
    
    def __init__(
        self,
        app,
        cacheable_routes: Optional[Set[str]] = None,
        default_ttl: int = 300,  # 5 minutes
        cache_query_params: bool = True,
        exclude_headers: Optional[Set[str]] = None
    ):
        super().__init__(app)
        self.cacheable_routes = cacheable_routes or {
            "/api/v1/files/",
            "/api/v1/paths/",
            "/api/v1/health/"
        }
        self.default_ttl = default_ttl
        self.cache_query_params = cache_query_params
        self.exclude_headers = exclude_headers or {
            "authorization",
            "cookie",
            "set-cookie",
            "x-user-name",
            "x-event-id"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching logic"""
        
        # Only cache GET requests for configured routes
        if not self._should_cache_request(request):
            return await call_next(request)
        
        # Generate cache key
        cache_key_str = self._generate_cache_key(request)
        
        # Try to get cached response
        try:
            cached_response = await cache.get(cache_key_str)
            if cached_response:
                logger.debug(
                    "Cache hit for request",
                    path=request.url.path,
                    cache_key=cache_key_str
                )
                return self._create_response_from_cache(cached_response)
        
        except (CacheError, CircuitBreakerError) as e:
            logger.warning(
                "Cache retrieval failed",
                path=request.url.path,
                error=str(e)
            )
        
        # Cache miss - execute request
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time
        
        # Cache successful responses
        if self._should_cache_response(response):
            try:
                await self._cache_response(cache_key_str, response, processing_time)
                logger.debug(
                    "Response cached",
                    path=request.url.path,
                    cache_key=cache_key_str,
                    status_code=response.status_code,
                    processing_time_ms=round(processing_time * 1000, 2)
                )
            except (CacheError, CircuitBreakerError) as e:
                logger.warning(
                    "Failed to cache response",
                    path=request.url.path,
                    error=str(e)
                )
        
        return response
    
    def _should_cache_request(self, request: Request) -> bool:
        """Determine if request should be cached"""
        
        # Only cache GET requests
        if request.method != "GET":
            return False
        
        # Check if route is cacheable
        path = request.url.path.rstrip('/')
        
        # Exact match or prefix match for routes ending with /
        for cacheable_route in self.cacheable_routes:
            if cacheable_route.endswith('/'):
                if path.startswith(cacheable_route.rstrip('/')):
                    return True
            elif path == cacheable_route:
                return True
        
        return False
    
    def _should_cache_response(self, response: Response) -> bool:
        """Determine if response should be cached"""
        
        # Only cache successful responses
        if not (200 <= response.status_code < 300):
            return False
        
        # Don't cache responses with certain headers
        for header_name in ["cache-control", "expires"]:
            header_value = response.headers.get(header_name, "").lower()
            if any(directive in header_value for directive in ["no-cache", "no-store", "private"]):
                return False
        
        return True
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        
        key_parts = ["http_cache", request.url.path.strip('/')]
        
        # Include query parameters if enabled
        if self.cache_query_params and request.query_params:
            query_str = str(request.query_params)
            key_parts.append(query_str)
        
        # Include relevant headers (excluding sensitive ones)
        relevant_headers = []
        for name, value in request.headers.items():
            if name.lower() not in self.exclude_headers:
                relevant_headers.append(f"{name}:{value}")
        
        if relevant_headers:
            key_parts.append(":".join(sorted(relevant_headers)))
        
        return cache_key(*key_parts)
    
    async def _cache_response(
        self, 
        cache_key_str: str, 
        response: Response, 
        processing_time: float
    ):
        """Cache the response"""
        
        # Read response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Prepare cache data
        cache_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response_body.decode('utf-8', errors='ignore'),
            "content_type": response.headers.get("content-type", "application/json"),
            "cached_at": time.time(),
            "processing_time": processing_time
        }
        
        # Add cache headers
        cache_data["headers"]["x-cache"] = "HIT"
        cache_data["headers"]["x-cached-at"] = str(int(cache_data["cached_at"]))
        cache_data["headers"]["x-original-processing-time"] = str(round(processing_time * 1000, 2))
        
        # Cache with TTL based on route
        ttl = self._get_ttl_for_path(cache_key_str)
        await cache.set(cache_key_str, cache_data, ttl)
        
        # Recreate response body iterator
        response.body_iterator = self._create_body_iterator(response_body)
    
    def _create_response_from_cache(self, cached_data: dict) -> Response:
        """Create response from cached data"""
        
        # Add cache hit headers
        headers = cached_data.get("headers", {}).copy()
        headers["x-cache"] = "HIT"
        headers["x-cached-at"] = str(cached_data.get("cached_at", time.time()))
        headers["x-original-processing-time"] = str(cached_data.get("processing_time", 0))
        
        # Create response
        response = Response(
            content=cached_data.get("body", ""),
            status_code=cached_data.get("status_code", 200),
            headers=headers,
            media_type=cached_data.get("content_type", "application/json")
        )
        
        return response
    
    def _get_ttl_for_path(self, cache_key_str: str) -> timedelta:
        """Get TTL based on cache key/path"""
        
        # Different TTLs for different types of data
        if "health" in cache_key_str:
            return timedelta(seconds=30)  # Health checks change frequently
        elif "files" in cache_key_str:
            return timedelta(minutes=5)   # File lists change moderately
        elif "paths" in cache_key_str:
            return timedelta(minutes=15)  # Paths change infrequently
        else:
            return timedelta(seconds=self.default_ttl)
    
    @staticmethod
    async def _create_body_iterator(body: bytes):
        """Create async iterator for response body"""
        yield body


class CacheInvalidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic cache invalidation on data modifications.
    
    Clears relevant cache entries when POST, PUT, PATCH, DELETE requests succeed.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.invalidation_patterns = {
            "files": ["http_cache:*files*", "http_cache:*health*"],
            "paths": ["http_cache:*paths*", "http_cache:*health*"],
            "upload": ["http_cache:*files*", "http_cache:*health*"]
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with cache invalidation logic"""
        
        response = await call_next(request)
        
        # Only invalidate on successful modifications
        if request.method in ["POST", "PUT", "PATCH", "DELETE"] and 200 <= response.status_code < 300:
            await self._invalidate_related_cache(request)
        
        return response
    
    async def _invalidate_related_cache(self, request: Request):
        """Invalidate cache entries related to the modified resource"""
        
        path = request.url.path.lower()
        patterns_to_clear = []
        
        # Determine what cache patterns to clear based on the request path
        for resource_type, patterns in self.invalidation_patterns.items():
            if resource_type in path:
                patterns_to_clear.extend(patterns)
                break
        
        # Default invalidation for unmatched paths
        if not patterns_to_clear:
            patterns_to_clear = ["http_cache:*"]
        
        # Clear cache patterns
        for pattern in patterns_to_clear:
            try:
                cleared_count = await cache.clear_pattern(pattern)
                logger.debug(
                    "Cache invalidated after modification",
                    path=request.url.path,
                    method=request.method,
                    pattern=pattern,
                    cleared_keys=cleared_count
                )
            except (CacheError, CircuitBreakerError) as e:
                logger.warning(
                    "Failed to invalidate cache",
                    path=request.url.path,
                    pattern=pattern,
                    error=str(e)
                )


# Cache control utilities
class CacheControl:
    """Utilities for cache control headers and directives"""
    
    @staticmethod
    def no_cache() -> dict:
        """Headers to prevent caching"""
        return {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    
    @staticmethod
    def max_age(seconds: int) -> dict:
        """Headers for max-age caching"""
        return {
            "Cache-Control": f"public, max-age={seconds}"
        }
    
    @staticmethod
    def private_cache(seconds: int) -> dict:
        """Headers for private caching"""
        return {
            "Cache-Control": f"private, max-age={seconds}"
        }
    
    @staticmethod
    def etag(value: str) -> dict:
        """Headers for ETag-based caching"""
        return {
            "ETag": f'"{value}"',
            "Cache-Control": "must-revalidate"
        }