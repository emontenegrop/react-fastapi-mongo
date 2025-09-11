"""Circuit breaker implementation for resilient external service calls"""

import asyncio
import time
from typing import Callable, Any, Optional, Dict
from enum import Enum
from dataclasses import dataclass, field
import httpx
from app.utils.structured_logger import get_logger

logger = get_logger("circuit_breaker")


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring"""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    total_requests: int = 0
    state_changes: int = 0
    
    def reset(self):
        """Reset failure counter but keep total stats"""
        self.failure_count = 0
        self.last_failure_time = None


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation with exponential backoff.
    
    The circuit breaker prevents cascading failures by stopping calls to
    failing services and allowing them time to recover.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = httpx.RequestError,
        success_threshold: int = 2  # Successes needed to close circuit from half-open
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        
        logger.info(
            "Circuit breaker initialized",
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function call through the circuit breaker.
        
        Args:
            func: Function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            CircuitBreakerError: If circuit is open
            Original exception: If function call fails
        """
        async with self._lock:
            self.stats.total_requests += 1
            
            # Check if circuit should be opened
            if self.state == CircuitState.CLOSED and self._should_open_circuit():
                await self._open_circuit()
            
            # Check if circuit should move to half-open
            elif self.state == CircuitState.OPEN and self._should_attempt_reset():
                await self._half_open_circuit()
            
            # Fail fast if circuit is open
            if self.state == CircuitState.OPEN:
                logger.warning(
                    "Circuit breaker open - failing fast",
                    name=self.name,
                    failure_count=self.stats.failure_count
                )
                raise CircuitBreakerError(f"Circuit breaker '{self.name}' is open")
        
        # Execute the function call
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
            
        except self.expected_exception as e:
            await self._on_failure()
            raise e
        except Exception as e:
            # Don't count unexpected exceptions as circuit breaker failures
            logger.error(
                "Unexpected error in circuit breaker call",
                name=self.name,
                error=str(e),
                error_type=type(e).__name__
            )
            raise e
    
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            self.stats.success_count += 1
            self.stats.last_success_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                if self.stats.success_count >= self.success_threshold:
                    await self._close_circuit()
            
            logger.debug(
                "Circuit breaker call succeeded",
                name=self.name,
                state=self.state.value,
                success_count=self.stats.success_count
            )
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self.stats.failure_count += 1
            self.stats.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                # Go back to open state
                await self._open_circuit()
            
            logger.warning(
                "Circuit breaker call failed",
                name=self.name,
                state=self.state.value,
                failure_count=self.stats.failure_count
            )
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened"""
        return self.stats.failure_count >= self.failure_threshold
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.stats.last_failure_time is None:
            return False
        return time.time() - self.stats.last_failure_time >= self.recovery_timeout
    
    async def _open_circuit(self):
        """Open the circuit"""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.stats.state_changes += 1
            logger.warning(
                "Circuit breaker opened",
                name=self.name,
                failure_count=self.stats.failure_count,
                recovery_timeout=self.recovery_timeout
            )
    
    async def _half_open_circuit(self):
        """Move circuit to half-open state"""
        self.state = CircuitState.HALF_OPEN
        self.stats.success_count = 0  # Reset success counter for half-open state
        self.stats.state_changes += 1
        logger.info(
            "Circuit breaker half-opened - testing recovery",
            name=self.name
        )
    
    async def _close_circuit(self):
        """Close the circuit"""
        self.state = CircuitState.CLOSED
        self.stats.reset()
        self.stats.state_changes += 1
        logger.info(
            "Circuit breaker closed - service recovered",
            name=self.name
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.stats.failure_count,
            "success_count": self.stats.success_count,
            "total_requests": self.stats.total_requests,
            "state_changes": self.stats.state_changes,
            "last_failure_time": self.stats.last_failure_time,
            "last_success_time": self.stats.last_success_time,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout
        }
    
    async def force_open(self):
        """Force circuit to open state (for testing/maintenance)"""
        async with self._lock:
            await self._open_circuit()
            logger.warning("Circuit breaker manually opened", name=self.name)
    
    async def force_close(self):
        """Force circuit to close state (for testing/recovery)"""
        async with self._lock:
            await self._close_circuit()
            logger.info("Circuit breaker manually closed", name=self.name)


class CircuitBreakerManager:
    """Manages multiple circuit breakers"""
    
    def __init__(self):
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.logger = get_logger("circuit_breaker_manager")
    
    def get_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = httpx.RequestError,
        success_threshold: int = 2
    ) -> CircuitBreaker:
        """
        Get or create a circuit breaker.
        
        Args:
            name: Unique name for the circuit breaker
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type that triggers circuit breaker
            success_threshold: Successes needed to close circuit from half-open
            
        Returns:
            CircuitBreaker instance
        """
        if name not in self._circuit_breakers:
            self._circuit_breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                expected_exception=expected_exception,
                success_threshold=success_threshold
            )
            self.logger.info("Created new circuit breaker", name=name)
        
        return self._circuit_breakers[name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        return {name: cb.get_stats() for name, cb in self._circuit_breakers.items()}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of all circuit breakers"""
        stats = self.get_all_stats()
        open_circuits = [name for name, stat in stats.items() if stat["state"] == "open"]
        
        return {
            "total_circuits": len(self._circuit_breakers),
            "open_circuits": len(open_circuits),
            "open_circuit_names": open_circuits,
            "healthy": len(open_circuits) == 0,
            "stats": stats
        }


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()


def with_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = httpx.RequestError
):
    """
    Decorator to wrap function calls with circuit breaker protection.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening circuit
        recovery_timeout: Recovery timeout in seconds
        expected_exception: Exception type that triggers circuit breaker
    """
    def decorator(func: Callable):
        circuit_breaker = circuit_breaker_manager.get_circuit_breaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception
        )
        
        async def wrapper(*args, **kwargs):
            return await circuit_breaker.call(func, *args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.circuit_breaker = circuit_breaker
        
        return wrapper
    return decorator