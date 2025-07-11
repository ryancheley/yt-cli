"""Tests for performance monitoring and benchmarking utilities."""

import asyncio
import time
from unittest.mock import Mock, patch

import pytest

from youtrack_cli.performance import (
    BenchmarkResult,
    PerformanceMetrics,
    PerformanceMonitor,
    benchmark_requests,
    get_performance_monitor,
    performance_timer,
)


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass."""

    def test_performance_metrics_creation(self):
        """Test creating performance metrics."""
        now = time.time()
        metadata = {"project": "TEST", "user": "testuser"}

        metrics = PerformanceMetrics(
            operation="fetch_issues", duration=1.5, success=True, timestamp=now, metadata=metadata
        )

        assert metrics.operation == "fetch_issues"
        assert metrics.duration == 1.5
        assert metrics.success is True
        assert metrics.timestamp == now
        assert metrics.metadata == metadata

    def test_performance_metrics_with_failure(self):
        """Test creating performance metrics for failed operation."""
        metrics = PerformanceMetrics(
            operation="create_issue",
            duration=0.5,
            success=False,
            timestamp=time.time(),
            metadata={"error": "Permission denied"},
        )

        assert metrics.operation == "create_issue"
        assert metrics.success is False
        assert metrics.metadata["error"] == "Permission denied"


class TestBenchmarkResult:
    """Test BenchmarkResult dataclass."""

    def test_benchmark_result_creation(self):
        """Test creating benchmark result."""
        durations = [1.0, 1.2, 0.8, 1.1, 0.9]

        result = BenchmarkResult(
            operation="api_call",
            total_operations=5,
            successful_operations=4,
            failed_operations=1,
            total_duration=5.0,
            avg_duration=1.0,
            median_duration=1.0,
            min_duration=0.8,
            max_duration=1.2,
            operations_per_second=0.8,
            durations=durations,
        )

        assert result.operation == "api_call"
        assert result.total_operations == 5
        assert result.successful_operations == 4
        assert result.failed_operations == 1
        assert result.total_duration == 5.0
        assert result.avg_duration == 1.0
        assert result.median_duration == 1.0
        assert result.min_duration == 0.8
        assert result.max_duration == 1.2
        assert result.operations_per_second == 0.8
        assert result.durations == durations


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor()

    def test_monitor_initialization(self):
        """Test monitor initialization."""
        assert len(self.monitor._metrics) == 0

    def test_record_metric(self):
        """Test recording a performance metric."""
        self.monitor.record(operation="test_operation", duration=1.5, success=True, project="TEST")

        assert len(self.monitor._metrics) == 1
        metric = self.monitor._metrics[0]
        assert metric.operation == "test_operation"
        assert metric.duration == 1.5
        assert metric.success is True
        assert metric.metadata["project"] == "TEST"

    def test_record_multiple_metrics(self):
        """Test recording multiple metrics."""
        self.monitor.record("op1", 1.0, True)
        self.monitor.record("op2", 2.0, False)
        self.monitor.record("op1", 1.5, True)

        assert len(self.monitor._metrics) == 3

    def test_get_metrics_all(self):
        """Test getting all metrics."""
        self.monitor.record("op1", 1.0, True)
        self.monitor.record("op2", 2.0, False)

        metrics = self.monitor.get_metrics()
        assert len(metrics) == 2

    def test_get_metrics_by_operation(self):
        """Test getting metrics filtered by operation."""
        self.monitor.record("op1", 1.0, True)
        self.monitor.record("op2", 2.0, False)
        self.monitor.record("op1", 1.5, True)

        op1_metrics = self.monitor.get_metrics(operation="op1")
        assert len(op1_metrics) == 2
        assert all(m.operation == "op1" for m in op1_metrics)

    def test_get_metrics_success_only(self):
        """Test getting only successful metrics."""
        self.monitor.record("op1", 1.0, True)
        self.monitor.record("op2", 2.0, False)
        self.monitor.record("op3", 1.5, True)

        success_metrics = self.monitor.get_metrics(success_only=True)
        assert len(success_metrics) == 2
        assert all(m.success for m in success_metrics)

    def test_get_metrics_operation_and_success(self):
        """Test getting metrics filtered by operation and success."""
        self.monitor.record("op1", 1.0, True)
        self.monitor.record("op1", 2.0, False)
        self.monitor.record("op2", 1.5, True)

        filtered_metrics = self.monitor.get_metrics(operation="op1", success_only=True)
        assert len(filtered_metrics) == 1
        assert filtered_metrics[0].operation == "op1"
        assert filtered_metrics[0].success is True

    def test_clear_metrics(self):
        """Test clearing all metrics."""
        self.monitor.record("op1", 1.0, True)
        self.monitor.record("op2", 2.0, False)

        assert len(self.monitor._metrics) == 2

        self.monitor.clear()

        assert len(self.monitor._metrics) == 0

    def test_summary_empty_monitor(self):
        """Test summary for empty monitor."""
        summary = self.monitor.summary()

        expected = {
            "operation": "all",
            "total_operations": 0,
            "total_duration": 0.0,
            "avg_duration": 0.0,
            "median_duration": 0.0,
        }
        assert summary == expected

    def test_summary_with_metrics(self):
        """Test summary with recorded metrics."""
        self.monitor.record("op1", 1.0, True)
        self.monitor.record("op1", 2.0, True)
        self.monitor.record("op1", 3.0, True)

        summary = self.monitor.summary(operation="op1")

        assert summary["operation"] == "op1"
        assert summary["total_operations"] == 3
        assert summary["successful_operations"] == 3
        assert summary["failed_operations"] == 0
        assert summary["total_duration"] == 6.0
        assert summary["avg_duration"] == 2.0
        assert summary["median_duration"] == 2.0
        assert summary["min_duration"] == 1.0
        assert summary["max_duration"] == 3.0
        assert summary["operations_per_second"] == 0.5  # 3 ops / 6 seconds

    def test_summary_with_failed_operations(self):
        """Test summary including failed operations."""
        self.monitor.record("op1", 1.0, True)
        self.monitor.record("op1", 2.0, False)  # Failed operation
        self.monitor.record("op1", 3.0, True)

        summary = self.monitor.summary(operation="op1")

        assert summary["successful_operations"] == 2  # Only successful ones
        assert summary["failed_operations"] == 1


class TestPerformanceTimer:
    """Test performance_timer context manager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor()

    @pytest.mark.asyncio
    async def test_performance_timer_success(self):
        """Test performance timer for successful operation."""
        async with performance_timer("test_operation", monitor=self.monitor):
            await asyncio.sleep(0.01)  # Simulate work

        metrics = self.monitor.get_metrics()
        assert len(metrics) == 1

        metric = metrics[0]
        assert metric.operation == "test_operation"
        assert metric.duration >= 0.01
        assert metric.success is True

    @pytest.mark.asyncio
    async def test_performance_timer_with_exception(self):
        """Test performance timer when operation raises exception."""
        with pytest.raises(ValueError):
            async with performance_timer("failing_operation", monitor=self.monitor):
                await asyncio.sleep(0.01)
                raise ValueError("Test error")

        metrics = self.monitor.get_metrics()
        assert len(metrics) == 1

        metric = metrics[0]
        assert metric.operation == "failing_operation"
        assert metric.duration >= 0.01
        assert metric.success is False

    @pytest.mark.asyncio
    async def test_performance_timer_with_metadata(self):
        """Test performance timer with metadata."""
        async with performance_timer("test_operation", monitor=self.monitor, project="TEST", user="testuser"):
            await asyncio.sleep(0.01)

        metric = self.monitor.get_metrics()[0]
        assert metric.metadata["project"] == "TEST"
        assert metric.metadata["user"] == "testuser"

    @pytest.mark.asyncio
    async def test_performance_timer_global_monitor(self):
        """Test performance timer with global monitor."""
        # Mock the global monitor
        with patch("youtrack_cli.performance._monitor") as mock_monitor:
            mock_record = Mock()
            mock_monitor.record = mock_record

            async with performance_timer("test_operation"):
                await asyncio.sleep(0.01)

            # Verify the global monitor's record method was called
            mock_record.assert_called_once()


class TestBenchmarkRequests:
    """Test benchmark_requests function."""

    @pytest.mark.asyncio
    async def test_benchmark_simple_function(self):
        """Test benchmarking a simple async function."""
        call_count = 0

        async def test_function():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return "result"

        result = await benchmark_requests(
            operation_name="test_benchmark", async_func=test_function, iterations=3, concurrent=1, warmup_iterations=0
        )

        assert isinstance(result, BenchmarkResult)
        assert result.operation == "test_benchmark"
        assert result.total_operations == 3
        assert result.successful_operations == 3
        assert result.failed_operations == 0
        assert len(result.durations) == 3
        assert all(d >= 0.01 for d in result.durations)
        assert result.avg_duration >= 0.01
        assert result.operations_per_second > 0
        assert call_count == 3  # No warmup, so only 3 calls

    @pytest.mark.asyncio
    async def test_benchmark_with_warmup(self):
        """Test benchmarking with warmup iterations."""
        call_count = 0

        async def test_function():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)

        result = await benchmark_requests(
            operation_name="test_benchmark", async_func=test_function, iterations=2, concurrent=1, warmup_iterations=1
        )

        assert result.total_operations == 2
        assert result.successful_operations == 2
        assert len(result.durations) == 2
        assert call_count == 3  # 1 warmup + 2 actual

    @pytest.mark.asyncio
    async def test_benchmark_with_failures(self):
        """Test benchmarking function that sometimes fails."""
        call_count = 0

        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:  # Fail every second call
                raise ValueError("Test error")
            await asyncio.sleep(0.001)

        result = await benchmark_requests(
            operation_name="failing_benchmark",
            async_func=failing_function,
            iterations=4,
            concurrent=1,
            warmup_iterations=0,
        )

        assert result.total_operations == 4
        assert result.successful_operations == 2
        assert result.failed_operations == 2
        assert len(result.durations) == 4

    @pytest.mark.asyncio
    async def test_benchmark_concurrent_requests(self):
        """Test benchmarking with concurrent requests."""
        call_count = 0

        async def test_function():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)

        result = await benchmark_requests(
            operation_name="concurrent_benchmark",
            async_func=test_function,
            iterations=2,
            concurrent=3,  # 3 concurrent calls per iteration
            warmup_iterations=0,
        )

        assert result.total_operations == 2
        assert result.successful_operations == 2
        assert len(result.durations) == 2
        assert call_count == 6  # 2 iterations * 3 concurrent = 6 calls

    @pytest.mark.asyncio
    async def test_benchmark_statistics_calculation(self):
        """Test that benchmark statistics are calculated correctly."""
        durations = []

        async def timed_function():
            duration = 0.01 + len(durations) * 0.005  # Increasing durations
            durations.append(duration)
            await asyncio.sleep(duration)

        result = await benchmark_requests(
            operation_name="stats_test", async_func=timed_function, iterations=3, concurrent=1, warmup_iterations=0
        )

        assert result.total_operations == 3
        assert result.min_duration == min(result.durations)
        assert result.max_duration == max(result.durations)
        assert abs(result.avg_duration - sum(result.durations) / len(result.durations)) < 0.001
        assert result.operations_per_second == result.successful_operations / result.total_duration


class TestGlobalPerformanceMonitor:
    """Test global performance monitor functionality."""

    def test_get_performance_monitor_singleton(self):
        """Test that get_performance_monitor returns singleton."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()

        assert monitor1 is monitor2
        assert isinstance(monitor1, PerformanceMonitor)

    def test_global_monitor_state_persistence(self):
        """Test that global monitor maintains state across calls."""
        monitor = get_performance_monitor()
        monitor.record("test_op", 1.0, True)

        # Get monitor again and verify state persists
        monitor2 = get_performance_monitor()
        metrics = monitor2.get_metrics()

        assert len(metrics) == 1
        assert metrics[0].operation == "test_op"


class TestPerformanceIntegration:
    """Test integration between performance components."""

    @pytest.mark.asyncio
    async def test_timer_with_custom_monitor(self):
        """Test performance timer with custom monitor."""
        custom_monitor = PerformanceMonitor()

        async with performance_timer("integration_test", monitor=custom_monitor, test_tag="value"):
            await asyncio.sleep(0.01)

        metrics = custom_monitor.get_metrics()
        assert len(metrics) == 1
        assert metrics[0].operation == "integration_test"
        assert metrics[0].metadata["test_tag"] == "value"
        assert metrics[0].success is True

    @pytest.mark.asyncio
    async def test_benchmark_with_timer_monitored_function(self):
        """Test benchmarking a function that uses performance timer internally."""
        internal_monitor = PerformanceMonitor()

        async def monitored_function():
            async with performance_timer("internal_op", monitor=internal_monitor):
                await asyncio.sleep(0.001)
                return "result"

        benchmark_result = await benchmark_requests(
            operation_name="benchmark_monitored",
            async_func=monitored_function,
            iterations=2,
            concurrent=1,
            warmup_iterations=0,
        )

        # Check benchmark results
        assert benchmark_result.successful_operations == 2

        # Check internal monitoring
        internal_metrics = internal_monitor.get_metrics()
        assert len(internal_metrics) == 2  # One for each iteration
        assert all(m.operation == "internal_op" for m in internal_metrics)

    def test_monitor_summary_with_mixed_operations(self):
        """Test monitor summary with multiple operation types."""
        monitor = PerformanceMonitor()

        # Record metrics for different operations
        monitor.record("fetch_issues", 1.0, True, project="PROJ1")
        monitor.record("fetch_issues", 1.5, True, project="PROJ2")
        monitor.record("create_issue", 2.0, True, project="PROJ1")
        monitor.record("create_issue", 1.8, False, project="PROJ1")  # Failed

        # Test overall summary
        overall_summary = monitor.summary()
        assert overall_summary["total_operations"] == 3  # Only successful ones
        assert overall_summary["failed_operations"] == 1

        # Test operation-specific summaries
        fetch_summary = monitor.summary(operation="fetch_issues")
        assert fetch_summary["total_operations"] == 2
        assert fetch_summary["failed_operations"] == 0

        create_summary = monitor.summary(operation="create_issue")
        assert create_summary["total_operations"] == 1  # Only successful
        assert create_summary["failed_operations"] == 1
