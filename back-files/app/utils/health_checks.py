"""Advanced health checks for system monitoring"""

import asyncio
import time
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from app.config.settings import settings
from app.db.database import client, db
from app.utils.cache import cache, CacheError, CircuitBreakerError
from app.utils.structured_logger import get_logger
from app.utils.circuit_breaker import circuit_breaker_manager

logger = get_logger("health_checks")

class HealthStatus(str, Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class HealthCheck:
    """Base class for health checks"""
    
    def __init__(self, name: str, critical: bool = False, timeout: int = 5):
        self.name = name
        self.critical = critical
        self.timeout = timeout
    
    async def check(self) -> Dict[str, Any]:
        """Execute the health check"""
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(self._check_implementation(), timeout=self.timeout)
            duration = time.time() - start_time
            
            return {
                "name": self.name,
                "status": result.get("status", HealthStatus.HEALTHY),
                "message": result.get("message", "Check passed"),
                "data": result.get("data", {}),
                "duration_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat(),
                "critical": self.critical
            }
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.warning(f"Health check '{self.name}' timed out", timeout=self.timeout)
            return {
                "name": self.name,
                "status": HealthStatus.CRITICAL if self.critical else HealthStatus.UNHEALTHY,
                "message": f"Check timed out after {self.timeout}s",
                "data": {},
                "duration_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat(),
                "critical": self.critical
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Health check '{self.name}' failed", error=str(e))
            return {
                "name": self.name,
                "status": HealthStatus.CRITICAL if self.critical else HealthStatus.UNHEALTHY,
                "message": f"Check failed: {str(e)}",
                "data": {"error": str(e)},
                "duration_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat(),
                "critical": self.critical
            }
    
    async def _check_implementation(self) -> Dict[str, Any]:
        """Override this method to implement the actual check"""
        raise NotImplementedError


class DatabaseHealthCheck(HealthCheck):
    """MongoDB database connectivity and performance check"""
    
    def __init__(self):
        super().__init__("database", critical=True, timeout=5)
    
    async def _check_implementation(self) -> Dict[str, Any]:
        """Check MongoDB connection and basic operations"""
        
        # Test connection
        start_time = time.time()
        await client.admin.command('ping')
        connection_time = time.time() - start_time
        
        # Test database access
        start_time = time.time()
        collections = await db.list_collection_names()
        query_time = time.time() - start_time
        
        # Get database stats
        db_stats = await db.command("dbStats")
        
        # Check if collections exist
        expected_collections = ["files", "paths"]
        missing_collections = [col for col in expected_collections if col not in collections]
        
        if missing_collections:
            return {
                "status": HealthStatus.DEGRADED,
                "message": f"Missing collections: {missing_collections}",
                "data": {
                    "connection_time_ms": round(connection_time * 1000, 2),
                    "query_time_ms": round(query_time * 1000, 2),
                    "collections": collections,
                    "missing_collections": missing_collections,
                    "db_size_mb": round(db_stats.get("dataSize", 0) / 1024 / 1024, 2)
                }
            }
        
        # Check performance thresholds
        status = HealthStatus.HEALTHY
        message = "Database is healthy"
        
        if connection_time > 1.0:  # 1 second threshold
            status = HealthStatus.DEGRADED
            message = "Database connection is slow"
        elif query_time > 0.5:  # 500ms threshold
            status = HealthStatus.DEGRADED
            message = "Database queries are slow"
        
        return {
            "status": status,
            "message": message,
            "data": {
                "connection_time_ms": round(connection_time * 1000, 2),
                "query_time_ms": round(query_time * 1000, 2),
                "collections": collections,
                "db_size_mb": round(db_stats.get("dataSize", 0) / 1024 / 1024, 2),
                "documents_count": db_stats.get("objects", 0),
                "indexes_count": db_stats.get("indexes", 0)
            }
        }


class CacheHealthCheck(HealthCheck):
    """Redis cache connectivity and performance check"""
    
    def __init__(self):
        super().__init__("cache", critical=False, timeout=3)
    
    async def _check_implementation(self) -> Dict[str, Any]:
        """Check Redis cache connection and operations"""
        
        try:
            # Test basic operations
            test_key = "health_check_test"
            test_value = {"timestamp": time.time(), "check": "health"}
            
            # Set operation
            start_time = time.time()
            await cache.set(test_key, test_value, 10)
            set_time = time.time() - start_time
            
            # Get operation  
            start_time = time.time()
            retrieved_value = await cache.get(test_key)
            get_time = time.time() - start_time
            
            # Delete operation
            start_time = time.time()
            await cache.delete(test_key)
            delete_time = time.time() - start_time
            
            # Get cache stats
            stats = await cache.get_stats()
            
            # Verify operations worked
            if retrieved_value != test_value:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Cache data integrity check failed",
                    "data": {
                        "expected": test_value,
                        "retrieved": retrieved_value
                    }
                }
            
            # Check performance thresholds
            total_time = set_time + get_time + delete_time
            status = HealthStatus.HEALTHY
            message = "Cache is healthy"
            
            if total_time > 0.5:  # 500ms total threshold
                status = HealthStatus.DEGRADED
                message = "Cache operations are slow"
            
            return {
                "status": status,
                "message": message,
                "data": {
                    "set_time_ms": round(set_time * 1000, 2),
                    "get_time_ms": round(get_time * 1000, 2),
                    "delete_time_ms": round(delete_time * 1000, 2),
                    "total_time_ms": round(total_time * 1000, 2),
                    "redis_version": stats.get("redis_version"),
                    "used_memory": stats.get("used_memory_human"),
                    "connected_clients": stats.get("connected_clients"),
                    "keyspace_hits": stats.get("keyspace_hits", 0),
                    "keyspace_misses": stats.get("keyspace_misses", 0)
                }
            }
            
        except (CacheError, CircuitBreakerError) as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Cache service unavailable: {str(e)}",
                "data": {"error": str(e)}
            }


class FileSystemHealthCheck(HealthCheck):
    """File system health and storage check"""
    
    def __init__(self):
        super().__init__("filesystem", critical=False, timeout=3)
    
    async def _check_implementation(self) -> Dict[str, Any]:
        """Check file system health and storage availability"""
        
        # Get disk usage for the server path
        disk_usage = psutil.disk_usage(settings.SERVER_PATH)
        
        # Calculate percentages
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        used_percentage = (disk_usage.used / disk_usage.total) * 100
        
        # Determine status based on usage
        status = HealthStatus.HEALTHY
        message = "File system is healthy"
        
        if used_percentage > 95:
            status = HealthStatus.CRITICAL
            message = "File system is critically full"
        elif used_percentage > 85:
            status = HealthStatus.DEGRADED
            message = "File system is running low on space"
        elif used_percentage > 70:
            status = HealthStatus.DEGRADED
            message = "File system usage is high"
        
        # Test write access
        try:
            import tempfile
            import os
            
            test_file = os.path.join(settings.SERVER_PATH, ".health_check_write_test")
            start_time = time.time()
            
            with open(test_file, 'w') as f:
                f.write("health check test")
            
            # Read it back
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Clean up
            os.remove(test_file)
            write_time = time.time() - start_time
            
            if content != "health check test":
                raise Exception("File write/read integrity check failed")
            
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"File system write test failed: {str(e)}",
                "data": {
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "used_percentage": round(used_percentage, 2),
                    "write_error": str(e)
                }
            }
        
        return {
            "status": status,
            "message": message,
            "data": {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "used_percentage": round(used_percentage, 2),
                "write_time_ms": round(write_time * 1000, 2),
                "path": settings.SERVER_PATH
            }
        }


class SystemResourcesHealthCheck(HealthCheck):
    """System resources (CPU, Memory) health check"""
    
    def __init__(self):
        super().__init__("system_resources", critical=False, timeout=5)
    
    async def _check_implementation(self) -> Dict[str, Any]:
        """Check system CPU and memory usage"""
        
        # Get CPU usage (1 second average)
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # Determine status
        status = HealthStatus.HEALTHY
        message = "System resources are healthy"
        
        if cpu_percent > 95 or memory_percent > 95:
            status = HealthStatus.CRITICAL
            message = "System resources are critically high"
        elif cpu_percent > 80 or memory_percent > 85:
            status = HealthStatus.DEGRADED
            message = "System resources are high"
        
        return {
            "status": status,
            "message": message,
            "data": {
                "cpu_percent": round(cpu_percent, 2),
                "cpu_count": cpu_count,
                "load_average": load_avg,
                "memory_percent": round(memory_percent, 2),
                "memory_total_gb": round(memory_total_gb, 2),
                "memory_available_gb": round(memory_available_gb, 2),
                "memory_used_gb": round((memory_total_gb - memory_available_gb), 2)
            }
        }


class CircuitBreakerHealthCheck(HealthCheck):
    """Circuit breaker status check"""
    
    def __init__(self):
        super().__init__("circuit_breakers", critical=False, timeout=2)
    
    async def _check_implementation(self) -> Dict[str, Any]:
        """Check circuit breaker status"""
        
        health_status = await circuit_breaker_manager.health_check()
        
        if not health_status["healthy"]:
            status = HealthStatus.DEGRADED
            message = f"Circuit breakers open: {', '.join(health_status['open_circuit_names'])}"
        else:
            status = HealthStatus.HEALTHY
            message = "All circuit breakers are healthy"
        
        return {
            "status": status,
            "message": message,
            "data": health_status
        }


class HealthCheckManager:
    """Manages and executes all health checks"""
    
    def __init__(self):
        self.checks = [
            DatabaseHealthCheck(),
            CacheHealthCheck(),
            FileSystemHealthCheck(),
            SystemResourcesHealthCheck(),
            CircuitBreakerHealthCheck()
        ]
        self.last_check_time: Optional[datetime] = None
        self.last_results: Optional[Dict[str, Any]] = None
        self.check_interval = timedelta(seconds=30)  # Cache results for 30 seconds
    
    async def run_all_checks(self, force: bool = False) -> Dict[str, Any]:
        """
        Run all health checks and return comprehensive results.
        
        Args:
            force: Force running checks even if cached results are available
            
        Returns:
            Dict containing overall health status and individual check results
        """
        # Return cached results if recent enough
        if (not force and self.last_check_time and 
            datetime.now() - self.last_check_time < self.check_interval and 
            self.last_results):
            return self.last_results
        
        start_time = time.time()
        
        # Run all checks concurrently
        check_tasks = [check.check() for check in self.checks]
        check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # Process results
        results = []
        critical_failures = []
        unhealthy_count = 0
        degraded_count = 0
        
        for i, result in enumerate(check_results):
            if isinstance(result, Exception):
                # Handle unexpected exceptions
                check_result = {
                    "name": self.checks[i].name,
                    "status": HealthStatus.CRITICAL,
                    "message": f"Unexpected error: {str(result)}",
                    "data": {"error": str(result)},
                    "duration_ms": 0,
                    "timestamp": datetime.now().isoformat(),
                    "critical": self.checks[i].critical
                }
            else:
                check_result = result
            
            results.append(check_result)
            
            # Track failures
            if check_result["status"] == HealthStatus.CRITICAL:
                if check_result["critical"]:
                    critical_failures.append(check_result["name"])
            elif check_result["status"] == HealthStatus.UNHEALTHY:
                unhealthy_count += 1
            elif check_result["status"] == HealthStatus.DEGRADED:
                degraded_count += 1
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        overall_message = "All systems are healthy"
        
        if critical_failures:
            overall_status = HealthStatus.CRITICAL
            overall_message = f"Critical failures in: {', '.join(critical_failures)}"
        elif unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
            overall_message = f"{unhealthy_count} systems are unhealthy"
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
            overall_message = f"{degraded_count} systems are degraded"
        
        total_duration = time.time() - start_time
        
        # Compile final results
        final_results = {
            "overall_status": overall_status,
            "overall_message": overall_message,
            "timestamp": datetime.now().isoformat(),
            "total_duration_ms": round(total_duration * 1000, 2),
            "checks": results,
            "summary": {
                "total_checks": len(results),
                "healthy": len([r for r in results if r["status"] == HealthStatus.HEALTHY]),
                "degraded": degraded_count,
                "unhealthy": unhealthy_count,
                "critical": len([r for r in results if r["status"] == HealthStatus.CRITICAL]),
                "critical_failures": critical_failures
            }
        }
        
        # Cache results
        self.last_check_time = datetime.now()
        self.last_results = final_results
        
        # Log overall status
        logger.info(
            "Health check completed",
            overall_status=overall_status,
            total_checks=len(results),
            critical_failures=len(critical_failures),
            duration_ms=round(total_duration * 1000, 2)
        )
        
        return final_results
    
    async def run_single_check(self, check_name: str) -> Optional[Dict[str, Any]]:
        """
        Run a single health check by name.
        
        Args:
            check_name: Name of the check to run
            
        Returns:
            Check result or None if check not found
        """
        for check in self.checks:
            if check.name == check_name:
                return await check.check()
        return None
    
    def get_check_names(self) -> List[str]:
        """Get list of available health check names"""
        return [check.name for check in self.checks]


# Global health check manager instance
health_manager = HealthCheckManager()