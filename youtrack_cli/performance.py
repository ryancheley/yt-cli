"""Performance monitoring and benchmarking utilities."""

import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from statistics import mean, median
from typing import Any, Optional

from .logging import get_logger

__all__ = [
    "PerformanceMetrics",
    "BenchmarkResult",
    "performance_timer",
    "benchmark_requests",
    "PerformanceMonitor",
]

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation."""

    operation: str
    duration: float
    success: bool
    timestamp: float
    metadata: dict[str, Any]


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark."""

    operation: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    total_duration: float
    avg_duration: float
    median_duration: float
    min_duration: float
    max_duration: float
    operations_per_second: float
    durations: list[float]


class PerformanceMonitor:
    """Monitor and collect performance metrics."""

    def __init__(self):
        self._metrics: list[PerformanceMetrics] = []

    def record(self, operation: str, duration: float, success: bool = True, **metadata) -> None:
        """Record a performance metric.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
            success: Whether the operation was successful
            **metadata: Additional metadata
        """
        metric = PerformanceMetrics(
            operation=operation,
            duration=duration,
            success=success,
            timestamp=time.time(),
            metadata=metadata,
        )
        self._metrics.append(metric)

        logger.debug(
            "Performance metric recorded",
            operation=operation,
            duration=duration,
            success=success,
        )

    def get_metrics(
        self,
        operation: Optional[str] = None,
        success_only: bool = False,
    ) -> list[PerformanceMetrics]:
        """Get collected metrics.

        Args:
            operation: Filter by operation name
            success_only: Only return successful operations

        Returns:
            List of performance metrics
        """
        metrics = self._metrics

        if operation:
            metrics = [m for m in metrics if m.operation == operation]

        if success_only:
            metrics = [m for m in metrics if m.success]

        return metrics

    def clear(self) -> None:
        """Clear all collected metrics."""
        count = len(self._metrics)
        self._metrics.clear()
        logger.debug("Performance metrics cleared", count=count)

    def summary(self, operation: Optional[str] = None) -> dict[str, Any]:
        """Get a summary of performance metrics.

        Args:
            operation: Filter by operation name

        Returns:
            Dictionary with performance summary
        """
        metrics = self.get_metrics(operation, success_only=True)

        if not metrics:
            return {
                "operation": operation or "all",
                "total_operations": 0,
                "total_duration": 0.0,
                "avg_duration": 0.0,
                "median_duration": 0.0,
            }

        durations = [m.duration for m in metrics]
        total_duration = sum(durations)

        return {
            "operation": operation or "all",
            "total_operations": len(metrics),
            "successful_operations": len(metrics),
            "failed_operations": len(
                [m for m in self._metrics if not m.success and (not operation or m.operation == operation)]
            ),
            "total_duration": total_duration,
            "avg_duration": mean(durations),
            "median_duration": median(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "operations_per_second": (len(metrics) / total_duration if total_duration > 0 else 0),
        }


# Global performance monitor
_monitor = PerformanceMonitor()


@asynccontextmanager
async def performance_timer(
    operation: str, monitor: Optional[PerformanceMonitor] = None, **metadata
) -> AsyncGenerator[None, None]:
    """Context manager for timing operations.

    Args:
        operation: Name of the operation being timed
        monitor: Performance monitor to use (defaults to global)
        **metadata: Additional metadata to record

    Example:
        async with performance_timer("fetch_issues", project="PROJ"):
            issues = await fetch_issues()
    """
    monitor = monitor or _monitor
    start_time = time.time()
    success = True

    try:
        yield
    except Exception:
        success = False
        raise
    finally:
        duration = time.time() - start_time
        monitor.record(operation, duration, success, **metadata)


async def benchmark_requests(
    operation_name: str,
    async_func,
    iterations: int = 10,
    concurrent: int = 1,
    warmup_iterations: int = 2,
) -> BenchmarkResult:
    """Benchmark an async function with multiple iterations.

    Args:
        operation_name: Name of the operation being benchmarked
        async_func: Async function to benchmark
        iterations: Number of iterations to run
        concurrent: Number of concurrent operations
        warmup_iterations: Number of warmup iterations (not included in results)

    Returns:
        BenchmarkResult with timing statistics
    """
    logger.info(
        "Starting benchmark",
        operation=operation_name,
        iterations=iterations,
        concurrent=concurrent,
        warmup=warmup_iterations,
    )

    # Warmup iterations
    if warmup_iterations > 0:
        logger.debug("Running warmup iterations", count=warmup_iterations)
        for _ in range(warmup_iterations):
            try:
                if concurrent > 1:
                    tasks = [async_func() for _ in range(concurrent)]
                    await asyncio.gather(*tasks)
                else:
                    await async_func()
            except Exception as e:
                logger.warning("Warmup iteration failed", error=str(e))

    # Actual benchmark
    durations = []
    successful = 0
    failed = 0

    benchmark_start = time.time()

    for i in range(iterations):
        iteration_start = time.time()
        try:
            if concurrent > 1:
                tasks = [async_func() for _ in range(concurrent)]
                await asyncio.gather(*tasks)
            else:
                await async_func()
            successful += 1
        except Exception as e:
            logger.warning(
                "Benchmark iteration failed",
                iteration=i + 1,
                error=str(e),
            )
            failed += 1

        iteration_duration = time.time() - iteration_start
        durations.append(iteration_duration)

        logger.debug(
            "Benchmark iteration complete",
            iteration=i + 1,
            duration=iteration_duration,
        )

    total_duration = time.time() - benchmark_start

    result = BenchmarkResult(
        operation=operation_name,
        total_operations=iterations,
        successful_operations=successful,
        failed_operations=failed,
        total_duration=total_duration,
        avg_duration=mean(durations) if durations else 0,
        median_duration=median(durations) if durations else 0,
        min_duration=min(durations) if durations else 0,
        max_duration=max(durations) if durations else 0,
        operations_per_second=successful / total_duration if total_duration > 0 else 0,
        durations=durations,
    )

    logger.info(
        "Benchmark complete",
        operation=operation_name,
        successful=successful,
        failed=failed,
        avg_duration=result.avg_duration,
        ops_per_second=result.operations_per_second,
    )

    return result


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _monitor
