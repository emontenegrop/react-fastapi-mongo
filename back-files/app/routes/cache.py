"""Cache management API endpoints"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from app.utils.cache import cache, cache_manager, CacheError, CircuitBreakerError
from app.utils.structured_logger import get_logger
from app.config.settings import settings

router = APIRouter()
logger = get_logger("cache_api")


@router.get(
    "/cache/stats",
    summary="Get cache statistics",
    description="Get Redis cache statistics and performance metrics",
    response_description="Cache statistics including hit rate, memory usage, and connection info"
)
async def get_cache_stats():
    """Get comprehensive cache statistics"""
    try:
        stats = await cache.get_stats()
        
        # Calculate hit rate
        hits = stats.get("keyspace_hits", 0)
        misses = stats.get("keyspace_misses", 0)
        total_requests = hits + misses
        hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    **stats,
                    "hit_rate_percentage": round(hit_rate, 2),
                    "total_cache_requests": total_requests
                },
                "message": "Cache statistics retrieved successfully"
            }
        )
        
    except (CacheError, CircuitBreakerError) as e:
        logger.error("Failed to retrieve cache statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service unavailable"
        )
    except Exception as e:
        logger.error("Unexpected error retrieving cache stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/cache/health",
    summary="Check cache health",
    description="Check if Redis cache is available and responsive",
    response_description="Cache health status"
)
async def check_cache_health():
    """Check cache service health"""
    try:
        # Try a simple operation to test cache availability
        await cache.set("health_check", {"timestamp": "test", "status": "ok"}, 10)
        result = await cache.get("health_check")
        await cache.delete("health_check")
        
        is_healthy = result is not None
        
        return JSONResponse(
            status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "healthy" if is_healthy else "unhealthy",
                "service": "redis_cache",
                "message": "Cache is responsive" if is_healthy else "Cache is not responding"
            }
        )
        
    except (CacheError, CircuitBreakerError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "redis_cache",
                "message": "Cache service unavailable"
            }
        )
    except Exception as e:
        logger.error("Error checking cache health", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "service": "redis_cache",
                "message": "Health check failed"
            }
        )


@router.delete(
    "/cache/clear",
    summary="Clear cache",
    description="Clear all cached data or specific patterns",
    response_description="Cache clear operation result"
)
async def clear_cache(pattern: str = "*"):
    """
    Clear cache entries matching pattern.
    
    Args:
        pattern: Pattern to match keys for deletion (default: "*" for all keys)
    """
    try:
        # Security check - only allow safe patterns in production
        if not settings.DEBUG and pattern == "*":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clearing all cache is not allowed in production"
            )
        
        cleared_count = await cache.clear_pattern(pattern)
        
        logger.info(
            "Cache cleared via API",
            pattern=pattern,
            cleared_keys=cleared_count
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    "pattern": pattern,
                    "cleared_keys": cleared_count
                },
                "message": f"Cleared {cleared_count} cache entries matching pattern '{pattern}'"
            }
        )
        
    except HTTPException:
        raise
    except (CacheError, CircuitBreakerError) as e:
        logger.error("Failed to clear cache", pattern=pattern, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service unavailable"
        )
    except Exception as e:
        logger.error("Unexpected error clearing cache", pattern=pattern, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/cache/user/{user_id}",
    summary="Clear user cache",
    description="Clear all cached data for a specific user",
    response_description="User cache clear operation result"
)
async def clear_user_cache(user_id: str):
    """Clear all cache entries for a specific user"""
    try:
        await cache_manager.invalidate_user_cache(user_id)
        
        logger.info("User cache cleared via API", user_id=user_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    "user_id": user_id
                },
                "message": f"User cache cleared for user {user_id}"
            }
        )
        
    except (CacheError, CircuitBreakerError) as e:
        logger.error("Failed to clear user cache", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service unavailable"
        )
    except Exception as e:
        logger.error("Unexpected error clearing user cache", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/cache/file/{file_id}",
    summary="Clear file cache",
    description="Clear cached data for a specific file",
    response_description="File cache clear operation result"
)
async def clear_file_cache(file_id: str):
    """Clear cache entries for a specific file"""
    try:
        await cache_manager.invalidate_file_cache(file_id)
        
        logger.info("File cache cleared via API", file_id=file_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    "file_id": file_id
                },
                "message": f"File cache cleared for file {file_id}"
            }
        )
        
    except (CacheError, CircuitBreakerError) as e:
        logger.error("Failed to clear file cache", file_id=file_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service unavailable"
        )
    except Exception as e:
        logger.error("Unexpected error clearing file cache", file_id=file_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/cache/key/{key}",
    summary="Get cached value",
    description="Get value for a specific cache key",
    response_description="Cached value or null if not found"
)
async def get_cache_key(key: str):
    """Get value for a specific cache key (for debugging)"""
    try:
        # Security check - only allow in debug mode
        if not settings.DEBUG:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cache key access is only allowed in debug mode"
            )
        
        value = await cache.get(key)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    "key": key,
                    "value": value,
                    "exists": value is not None
                },
                "message": "Cache key retrieved successfully"
            }
        )
        
    except HTTPException:
        raise
    except (CacheError, CircuitBreakerError) as e:
        logger.error("Failed to get cache key", key=key, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service unavailable"
        )
    except Exception as e:
        logger.error("Unexpected error getting cache key", key=key, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )