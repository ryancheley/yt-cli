"""Tests for performance benchmarking utilities."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from youtrack_cli.performance_benchmark import FieldSelectionBenchmark, run_benchmark


class TestFieldSelectionBenchmark:
    """Test FieldSelectionBenchmark class."""

    def test_init(self):
        """Test benchmark initialization."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager") as mock_issue_manager:
            with patch("youtrack_cli.performance_benchmark.get_field_selector") as mock_field_selector:
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                assert benchmark.auth_manager == mock_auth_manager
                mock_issue_manager.assert_called_once_with(mock_auth_manager)
                mock_field_selector.assert_called_once()

    @pytest.mark.asyncio
    async def test_benchmark_profile_performance_success(self):
        """Test successful benchmark profile performance."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager") as mock_issue_manager_cls:
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                mock_issue_manager = Mock()
                mock_issue_manager.list_issues = AsyncMock(return_value={"status": "success", "issues": []})
                mock_issue_manager_cls.return_value = mock_issue_manager

                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                with patch("youtrack_cli.performance_benchmark.logger") as mock_logger:
                    # Need many time values: 3 profiles × (1 warmup + 5 iterations) × 2 time calls per run = 36 values
                    time_values = [i * 0.1 for i in range(50)]  # Generate enough time values
                    with patch("time.time", side_effect=time_values):
                        results = await benchmark.benchmark_profile_performance(
                            project_id="TEST", query="test query", sample_size=10
                        )

                # Should have results for all profiles
                assert "minimal" in results
                assert "standard" in results
                assert "full" in results

                # Each profile should have timing data
                for profile in ["minimal", "standard", "full"]:
                    assert "avg_time" in results[profile]
                    assert "min_time" in results[profile]
                    assert "max_time" in results[profile]
                    assert "times" in results[profile]
                    assert len(results[profile]["times"]) == 5  # 5 iterations

                # Verify logging
                mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_benchmark_profile_performance_with_defaults(self):
        """Test benchmark with default parameters."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager") as mock_issue_manager_cls:
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                mock_issue_manager = Mock()
                mock_issue_manager.list_issues = AsyncMock(return_value={"status": "success", "issues": []})
                mock_issue_manager_cls.return_value = mock_issue_manager

                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                with patch("time.time", side_effect=[i * 0.1 for i in range(50)]):
                    await benchmark.benchmark_profile_performance()

                # Should call list_issues with correct default parameters
                calls = mock_issue_manager.list_issues.call_args_list

                # Warm-up calls (3 profiles × 1 warm-up each) + benchmark calls (3 profiles × 5 iterations each)
                assert len(calls) == 18  # 3 + 15

                # Check some calls have default parameters
                for call in calls:
                    args, kwargs = call
                    assert kwargs.get("project_id") is None
                    assert kwargs.get("query") is None
                    assert kwargs.get("page_size") == 100 or kwargs.get("page_size") == 10  # warm-up vs benchmark
                    assert kwargs.get("top") == 100 or kwargs.get("top") == 10

    @pytest.mark.asyncio
    async def test_run_single_benchmark_success(self):
        """Test successful single benchmark run."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager") as mock_issue_manager_cls:
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                mock_issue_manager = Mock()
                mock_issue_manager.list_issues = AsyncMock(return_value={"status": "success", "issues": []})
                mock_issue_manager_cls.return_value = mock_issue_manager

                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                with patch("time.time", side_effect=[0.0, 0.5]):
                    duration = await benchmark._run_single_benchmark("TEST", "query", "minimal", 50)

                assert duration == 0.5
                mock_issue_manager.list_issues.assert_called_once_with(
                    project_id="TEST", query="query", field_profile="minimal", page_size=50, top=50
                )

    @pytest.mark.asyncio
    async def test_run_single_benchmark_failure(self):
        """Test single benchmark run with failure."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager") as mock_issue_manager_cls:
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                mock_issue_manager = Mock()
                mock_issue_manager.list_issues = AsyncMock(return_value={"status": "error", "message": "API error"})
                mock_issue_manager_cls.return_value = mock_issue_manager

                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                with pytest.raises(Exception, match="Benchmark failed: API error"):
                    await benchmark._run_single_benchmark("TEST", "query", "minimal", 50)

    def test_analyze_performance_gains_success(self):
        """Test performance gains analysis with all profiles."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager"):
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                results = {
                    "minimal": {"avg_time": 0.5},
                    "standard": {"avg_time": 0.8},
                    "full": {"avg_time": 1.0},
                }

                with patch("youtrack_cli.performance_benchmark.logger") as mock_logger:
                    improvements = benchmark.analyze_performance_gains(results)

                # Should calculate improvements correctly
                assert "minimal_vs_full" in improvements
                assert "standard_vs_full" in improvements
                assert "estimated_data_reduction" in improvements

                # Check calculations (use approximate comparison for floating point)
                assert abs(improvements["minimal_vs_full"] - 50.0) < 0.01  # (1.0 - 0.5) / 1.0 * 100
                assert abs(improvements["standard_vs_full"] - 20.0) < 0.01  # (1.0 - 0.8) / 1.0 * 100
                assert improvements["estimated_data_reduction"] == 75.0

                # Verify logging
                mock_logger.info.assert_called()

    def test_analyze_performance_gains_missing_profiles(self):
        """Test performance gains analysis with missing profiles."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager"):
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                # Missing full profile
                results = {
                    "minimal": {"avg_time": 0.5},
                    "standard": {"avg_time": 0.8},
                }

                improvements = benchmark.analyze_performance_gains(results)

                # Should return empty dict
                assert improvements == {}

    def test_analyze_performance_gains_zero_full_time(self):
        """Test performance gains analysis with zero full time."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager"):
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                results = {
                    "minimal": {"avg_time": 0.5},
                    "standard": {"avg_time": 0.8},
                    "full": {"avg_time": 0.0},  # Zero time
                }

                improvements = benchmark.analyze_performance_gains(results)

                # Should return empty dict due to zero division protection
                assert improvements == {}

    def test_analyze_performance_gains_partial_profiles(self):
        """Test performance gains analysis with only minimal and full."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager"):
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                results = {
                    "minimal": {"avg_time": 0.3},
                    "full": {"avg_time": 1.0},
                    # No standard profile
                }

                with patch("youtrack_cli.performance_benchmark.logger"):
                    improvements = benchmark.analyze_performance_gains(results)

                # Should calculate minimal vs full but not standard vs full
                assert "minimal_vs_full" in improvements
                assert "standard_vs_full" not in improvements
                assert improvements["minimal_vs_full"] == 70.0

    def test_print_benchmark_report(self):
        """Test benchmark report printing."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager"):
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                results = {
                    "minimal": {"avg_time": 0.5, "min_time": 0.4, "max_time": 0.6},
                    "standard": {"avg_time": 0.8, "min_time": 0.7, "max_time": 0.9},
                    "full": {"avg_time": 1.0, "min_time": 0.9, "max_time": 1.1},
                }

                with patch("builtins.print") as mock_print:
                    benchmark.print_benchmark_report(results)

                # Should print report sections
                printed_content = "".join(str(call) for call in mock_print.call_args_list)
                assert "FIELD SELECTION PERFORMANCE BENCHMARK REPORT" in printed_content
                assert "PERFORMANCE IMPROVEMENTS" in printed_content
                assert "RECOMMENDATIONS" in printed_content
                assert "minimal" in printed_content.lower()
                assert "standard" in printed_content.lower()
                assert "full" in printed_content.lower()

    def test_print_benchmark_report_no_improvements(self):
        """Test benchmark report printing with no improvements."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager"):
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                # Mock analyze_performance_gains to return empty
                with patch.object(benchmark, "analyze_performance_gains", return_value={}):
                    results = {
                        "minimal": {"avg_time": 0.5, "min_time": 0.4, "max_time": 0.6},
                    }

                    with patch("builtins.print") as mock_print:
                        benchmark.print_benchmark_report(results)

                    # Should print basic report but no improvements section
                    printed_content = "".join(str(call) for call in mock_print.call_args_list)
                    assert "FIELD SELECTION PERFORMANCE BENCHMARK REPORT" in printed_content
                    assert "RECOMMENDATIONS" in printed_content
                    # Should not have performance improvements section
                    assert "PERFORMANCE IMPROVEMENTS" not in printed_content


class TestRunBenchmark:
    """Test run_benchmark function."""

    @pytest.mark.asyncio
    async def test_run_benchmark_success(self):
        """Test successful benchmark run."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.FieldSelectionBenchmark") as mock_benchmark_cls:
            mock_benchmark = Mock()
            mock_benchmark.benchmark_profile_performance = AsyncMock(
                return_value={
                    "minimal": {"avg_time": 0.5, "min_time": 0.4, "max_time": 0.6},
                    "full": {"avg_time": 1.0, "min_time": 0.9, "max_time": 1.1},
                }
            )
            mock_benchmark.print_benchmark_report = Mock()
            mock_benchmark_cls.return_value = mock_benchmark

            await run_benchmark(mock_auth_manager, project_id="TEST", sample_size=25)

            # Should create benchmark and run it
            mock_benchmark_cls.assert_called_once_with(mock_auth_manager)
            mock_benchmark.benchmark_profile_performance.assert_called_once_with(project_id="TEST", sample_size=25)
            mock_benchmark.print_benchmark_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_benchmark_with_defaults(self):
        """Test benchmark run with default parameters."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.FieldSelectionBenchmark") as mock_benchmark_cls:
            mock_benchmark = Mock()
            mock_benchmark.benchmark_profile_performance = AsyncMock(return_value={})
            mock_benchmark.print_benchmark_report = Mock()
            mock_benchmark_cls.return_value = mock_benchmark

            await run_benchmark(mock_auth_manager)

            # Should use default parameters
            mock_benchmark.benchmark_profile_performance.assert_called_once_with(project_id=None, sample_size=50)

    @pytest.mark.asyncio
    async def test_run_benchmark_failure(self):
        """Test benchmark run with failure."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.FieldSelectionBenchmark") as mock_benchmark_cls:
            mock_benchmark = Mock()
            mock_benchmark.benchmark_profile_performance = AsyncMock(side_effect=Exception("Benchmark error"))
            mock_benchmark_cls.return_value = mock_benchmark

            with patch("youtrack_cli.performance_benchmark.logger") as mock_logger:
                with patch("builtins.print") as mock_print:
                    with pytest.raises(Exception, match="Benchmark error"):
                        await run_benchmark(mock_auth_manager)

            # Should log error and print failure message
            mock_logger.error.assert_called_once()
            mock_print.assert_called_with("❌ Benchmark failed: Benchmark error")


class TestBenchmarkIntegration:
    """Integration tests for benchmark functionality."""

    @pytest.mark.asyncio
    async def test_full_benchmark_workflow(self):
        """Test complete benchmark workflow."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager") as mock_issue_manager_cls:
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                # Mock successful issue manager responses
                mock_issue_manager = Mock()
                mock_issue_manager.list_issues = AsyncMock(return_value={"status": "success", "issues": []})
                mock_issue_manager_cls.return_value = mock_issue_manager

                # Create benchmark
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                # Mock time to control benchmark duration
                time_values = [i * 0.1 for i in range(40)]  # Enough for all calls
                with patch("time.time", side_effect=time_values):
                    with patch("youtrack_cli.performance_benchmark.logger"):
                        # Run benchmark
                        results = await benchmark.benchmark_profile_performance(sample_size=10)

                        # Analyze results
                        improvements = benchmark.analyze_performance_gains(results)

                        # Print report (mock print to capture output)
                        with patch("builtins.print") as mock_print:
                            benchmark.print_benchmark_report(results)

                # Verify complete workflow
                assert len(results) == 3  # All profiles
                assert all(profile in results for profile in ["minimal", "standard", "full"])
                assert len(improvements) > 0  # Should have some improvements
                mock_print.assert_called()  # Report should be printed

    def test_benchmark_edge_cases(self):
        """Test benchmark with edge cases."""
        mock_auth_manager = Mock()

        with patch("youtrack_cli.performance_benchmark.IssueManager"):
            with patch("youtrack_cli.performance_benchmark.get_field_selector"):
                benchmark = FieldSelectionBenchmark(mock_auth_manager)

                # Test with empty results
                empty_results = {}
                improvements = benchmark.analyze_performance_gains(empty_results)
                assert improvements == {}

                # Test with malformed results
                malformed_results = {"minimal": {}}  # Missing avg_time
                improvements = benchmark.analyze_performance_gains(malformed_results)
                assert improvements == {}

                # Test with single profile
                single_results = {"minimal": {"avg_time": 0.5}}
                improvements = benchmark.analyze_performance_gains(single_results)
                assert improvements == {}
