"""Redis-based caching utilities with circuit breaker protection"""

import json
import asyncio
from typing import Any, Optional, Dict, List, Union
from datetime import timedelta
import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from app.config.settings import settings
from app.utils.circuit_breaker import with_circuit_breaker, CircuitBreakerError
from app.utils.structured_logger import get_logger

logger = get_logger("cache")

class CacheError(Exception):
    """Custom exception for cache operations"""
    pass

class RedisCache:
    """Redis cache client with circuit breaker protection and connection pooling"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.connection_pool: Optional[redis.ConnectionPool] = None
        self._initialized = False
        self.default_ttl = settings.CACHE_DEFAULT_TTL
        
    async def initialize(self):
        """Initialize Redis connection pool"""
        if self._initialized:
            return
            
        try:
            self.connection_pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                retry_on_timeout=True,
                decode_responses=False  # We'll handle encoding ourselves
            )
            
            self.client = redis.Redis(
                connection_pool=self.connection_pool,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30
            )
            
            # Test connection
            await self.client.ping()
            self._initialized = True
            
            logger.info(
                "Redis cache initialized successfully",
                redis_url=settings.redis_url,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                default_ttl=self.default_ttl
            )
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Failed to initialize Redis cache",
                error=str(e),
                redis_url=settings.redis_url
            )
            raise CacheError(f"Redis initialization failed: {e}")
    
    async def close(self):
        """Close Redis connection pool"""
        if self.client:
            await self.client.close()
        if self.connection_pool:
            await self.connection_pool.disconnect()
        self._initialized = False
        logger.info("Redis cache connection closed")

    @with_circuit_breaker(
        name="redis-cache",
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(RedisError, RedisConnectionError, CacheError)
    )
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with JSON deserialization"""
        if not self._initialized:
            await self.initialize()
            
        try:
            value = await self.client.get(key)
            if value is None:
                logger.debug("Cache miss", key=key)
                return None
                
            # Deserialize JSON
            try:
                result = json.loads(value.decode('utf-8'))
                logger.debug("Cache hit", key=key, data_type=type(result).__name__)
                return result
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(
                    "Failed to deserialize cached value",
                    key=key,
                    error=str(e)
                )
                # Delete corrupted cache entry
                await self.delete(key)
                return None
                
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Redis get operation failed",
                key=key,
                error=str(e)
            )
            raise CacheError(f"Cache get failed for key {key}: {e}")

    @with_circuit_breaker(
        name="redis-cache",
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(RedisError, RedisConnectionError, CacheError)
    )
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache with JSON serialization"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # Serialize to JSON
            try:
                serialized_value = json.dumps(value, default=str, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                logger.error(
                    "Failed to serialize value for caching",
                    key=key,
                    value_type=type(value).__name__,
                    error=str(e)
                )
                raise CacheError(f"Serialization failed for key {key}: {e}")
            
            # Set TTL
            if ttl is None:
                ttl = self.default_ttl
            elif isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            result = await self.client.setex(key, ttl, serialized_value.encode('utf-8'))
            
            logger.debug(
                "Value cached successfully",
                key=key,
                ttl=ttl,
                data_size=len(serialized_value)
            )
            
            return bool(result)
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Redis set operation failed",
                key=key,
                error=str(e)
            )
            raise CacheError(f"Cache set failed for key {key}: {e}")

    @with_circuit_breaker(
        name="redis-cache",
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(RedisError, RedisConnectionError, CacheError)
    )
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._initialized:
            await self.initialize()
            
        try:
            result = await self.client.delete(key)
            logger.debug("Cache key deleted", key=key, existed=bool(result))
            return bool(result)
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Redis delete operation failed",
                key=key,
                error=str(e)
            )
            raise CacheError(f"Cache delete failed for key {key}: {e}")

    @with_circuit_breaker(
        name="redis-cache",
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(RedisError, RedisConnectionError, CacheError)
    )
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._initialized:
            await self.initialize()
            
        try:
            result = await self.client.exists(key)
            return bool(result)
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Redis exists operation failed",
                key=key,
                error=str(e)
            )
            raise CacheError(f"Cache exists check failed for key {key}: {e}")

    @with_circuit_breaker(
        name="redis-cache",
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(RedisError, RedisConnectionError, CacheError)
    )
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        if not self._initialized:
            await self.initialize()
            
        try:
            values = await self.client.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        logger.warning(
                            "Failed to deserialize cached value in batch",
                            key=key,
                            error=str(e)
                        )
                        # Delete corrupted entry
                        await self.delete(key)
            
            logger.debug(
                "Batch cache operation completed",
                requested_keys=len(keys),
                found_keys=len(result)
            )
            
            return result
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Redis mget operation failed",
                keys=keys,
                error=str(e)
            )
            raise CacheError(f"Cache batch get failed: {e}")

    @with_circuit_breaker(
        name="redis-cache",
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(RedisError, RedisConnectionError, CacheError)
    )
    async def set_many(
        self, 
        mapping: Dict[str, Any], 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set multiple values in cache"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # Serialize all values
            serialized_mapping = {}
            for key, value in mapping.items():
                try:
                    serialized_mapping[key] = json.dumps(value, default=str, ensure_ascii=False).encode('utf-8')
                except (TypeError, ValueError) as e:
                    logger.error(
                        "Failed to serialize value in batch",
                        key=key,
                        value_type=type(value).__name__,
                        error=str(e)
                    )
                    continue
            
            if not serialized_mapping:
                logger.warning("No values to cache after serialization")
                return False
            
            # Set TTL
            if ttl is None:
                ttl = self.default_ttl
            elif isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            # Use pipeline for atomic operation
            pipe = self.client.pipeline()
            for key, value in serialized_mapping.items():
                pipe.setex(key, ttl, value)
            
            results = await pipe.execute()
            success_count = sum(1 for result in results if result)
            
            logger.debug(
                "Batch cache set completed",
                total_keys=len(serialized_mapping),
                successful_keys=success_count,
                ttl=ttl
            )
            
            return success_count == len(serialized_mapping)
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Redis batch set operation failed",
                keys=list(mapping.keys()),
                error=str(e)
            )
            raise CacheError(f"Cache batch set failed: {e}")

    @with_circuit_breaker(
        name="redis-cache",
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(RedisError, RedisConnectionError, CacheError)
    )
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self._initialized:
            await self.initialize()
            
        try:
            keys = await self.client.keys(pattern)
            if not keys:
                logger.debug("No keys found for pattern", pattern=pattern)
                return 0
            
            deleted_count = await self.client.delete(*keys)
            logger.info(
                "Cache pattern cleared",
                pattern=pattern,
                deleted_keys=deleted_count
            )
            
            return deleted_count
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Redis pattern clear operation failed",
                pattern=pattern,
                error=str(e)
            )
            raise CacheError(f"Cache pattern clear failed: {e}")

    @with_circuit_breaker(
        name="redis-cache",
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(RedisError, RedisConnectionError, CacheError)
    )
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self._initialized:
            await self.initialize()
            
        try:
            info = await self.client.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "redis_version": info.get("redis_version", "unknown")
            }
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                "Failed to get Redis stats",
                error=str(e)
            )
            raise CacheError(f"Cache stats retrieval failed: {e}")


# Global cache instance
cache = RedisCache()


def cache_key(*parts: str) -> str:
    """Generate cache key from parts"""
    return ":".join(str(part) for part in parts)


async def cached_result(
    key: str,
    fetch_func,
    ttl: Optional[Union[int, timedelta]] = None,
    *args,
    **kwargs
) -> Any:
    """
    Get cached result or fetch and cache new result.
    
    Args:
        key: Cache key
        fetch_func: Function to call if cache miss
        ttl: Time to live for cached result
        *args: Arguments for fetch_func
        **kwargs: Keyword arguments for fetch_func
    """
    try:
        # Try to get from cache
        result = await cache.get(key)
        if result is not None:
            return result
    except (CacheError, CircuitBreakerError):
        logger.warning("Cache unavailable, fetching fresh data", key=key)
    
    # Cache miss or error, fetch fresh data
    result = await fetch_func(*args, **kwargs) if asyncio.iscoroutinefunction(fetch_func) else fetch_func(*args, **kwargs)
    
    # Try to cache result
    try:
        await cache.set(key, result, ttl)
    except (CacheError, CircuitBreakerError):
        logger.warning("Failed to cache result", key=key)
    
    return result


class CacheManager:
    """High-level cache management utilities"""
    
    @staticmethod
    def file_cache_key(file_id: str) -> str:
        """Generate cache key for file data"""
        return cache_key("file", file_id)
    
    @staticmethod
    def path_cache_key(path_id: str) -> str:
        """Generate cache key for path data"""
        return cache_key("path", path_id)
    
    @staticmethod
    def user_files_cache_key(user_id: str, page: int = 1) -> str:
        """Generate cache key for user's files"""
        return cache_key("user_files", user_id, page)
    
    @staticmethod
    def file_list_cache_key(filters: Dict[str, Any]) -> str:
        """Generate cache key for file list with filters"""
        filter_str = ":".join(f"{k}={v}" for k, v in sorted(filters.items()) if v is not None)
        return cache_key("files", filter_str) if filter_str else cache_key("files", "all")
    
    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """Invalidate all cache entries for a user"""
        pattern = cache_key("user_files", user_id, "*")
        try:
            await cache.clear_pattern(pattern)
            logger.debug("User cache invalidated", user_id=user_id)
        except (CacheError, CircuitBreakerError):
            logger.warning("Failed to invalidate user cache", user_id=user_id)
    
    @staticmethod
    async def invalidate_file_cache(file_id: str):
        """Invalidate cache entries for a specific file"""
        try:
            await cache.delete(CacheManager.file_cache_key(file_id))
            # Also clear file lists cache
            await cache.clear_pattern(cache_key("files", "*"))
            logger.debug("File cache invalidated", file_id=file_id)
        except (CacheError, CircuitBreakerError):
            logger.warning("Failed to invalidate file cache", file_id=file_id)


# Cache manager instance
cache_manager = CacheManager()