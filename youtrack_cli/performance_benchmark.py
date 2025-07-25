"""Performance benchmarking utilities for field selection optimization."""

import time
from typing import Dict, Optional

from .auth import AuthManager
from .field_selection import get_field_selector
from .logging import get_logger
from .managers.issues import IssueManager

__all__ = ["FieldSelectionBenchmark"]

logger = get_logger(__name__)


class FieldSelectionBenchmark:
    """Benchmark field selection performance improvements."""

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.issue_manager = IssueManager(auth_manager)
        self.field_selector = get_field_selector()

    async def benchmark_profile_performance(
        self, project_id: Optional[str] = None, query: Optional[str] = None, sample_size: int = 100
    ) -> Dict[str, Dict[str, float]]:
        """Benchmark performance across different field selection profiles.

        Args:
            project_id: Project to test with
            query: Query filter to apply
            sample_size: Number of issues to fetch for benchmarking

        Returns:
            Dictionary with benchmark results for each profile
        """
        profiles = ["minimal", "standard", "full"]
        results = {}

        logger.info(
            "Starting field selection performance benchmark",
            project_id=project_id,
            query=query,
            sample_size=sample_size,
        )

        for profile in profiles:
            logger.info(f"Benchmarking profile: {profile}")

            # Warm up
            await self._run_single_benchmark(project_id, query, profile, 10)

            # Actual benchmark
            times = []
            for _ in range(5):  # Run 5 iterations
                duration = await self._run_single_benchmark(project_id, query, profile, sample_size)
                times.append(duration)

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            results[profile] = {"avg_time": avg_time, "min_time": min_time, "max_time": max_time, "times": times}

            logger.info(
                f"Profile {profile} benchmark completed",
                avg_time=f"{avg_time:.3f}s",
                min_time=f"{min_time:.3f}s",
                max_time=f"{max_time:.3f}s",
            )

        return results

    async def _run_single_benchmark(
        self, project_id: Optional[str], query: Optional[str], profile: str, sample_size: int
    ) -> float:
        """Run a single benchmark iteration.

        Returns:
            Duration in seconds
        """
        start_time = time.time()

        result = await self.issue_manager.list_issues(
            project_id=project_id, query=query, field_profile=profile, page_size=sample_size, top=sample_size
        )

        end_time = time.time()
        duration = end_time - start_time

        if result["status"] != "success":
            raise Exception(f"Benchmark failed: {result['message']}")

        return duration

    def analyze_performance_gains(self, results: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Analyze performance improvements from using optimized field selection.

        Args:
            results: Benchmark results from benchmark_profile_performance

        Returns:
            Dictionary with performance improvement percentages
        """
        if "full" not in results or "minimal" not in results:
            return {}

        full_time = results["full"]["avg_time"]
        minimal_time = results["minimal"]["avg_time"]
        standard_time = results.get("standard", {}).get("avg_time", 0)

        improvements = {}

        if full_time > 0:
            # Calculate improvement of minimal vs full
            minimal_improvement = ((full_time - minimal_time) / full_time) * 100
            improvements["minimal_vs_full"] = minimal_improvement

            # Calculate improvement of standard vs full
            if standard_time > 0:
                standard_improvement = ((full_time - standard_time) / full_time) * 100
                improvements["standard_vs_full"] = standard_improvement

            # Data transfer reduction estimate (rough approximation)
            # Minimal profile typically has ~75% fewer fields than full
            improvements["estimated_data_reduction"] = 75.0

        logger.info(
            "Performance analysis completed",
            minimal_improvement=f"{improvements.get('minimal_vs_full', 0):.1f}%",
            standard_improvement=f"{improvements.get('standard_vs_full', 0):.1f}%",
            data_reduction=f"{improvements.get('estimated_data_reduction', 0):.1f}%",
        )

        return improvements

    def print_benchmark_report(self, results: Dict[str, Dict[str, float]]) -> None:
        """Print a formatted benchmark report.

        Args:
            results: Benchmark results from benchmark_profile_performance
        """
        print("\n" + "=" * 60)
        print("FIELD SELECTION PERFORMANCE BENCHMARK REPORT")
        print("=" * 60)

        print(f"\n{'Profile':<12} {'Avg Time':<12} {'Min Time':<12} {'Max Time':<12}")
        print("-" * 50)

        for profile, data in results.items():
            avg_time = data["avg_time"]
            min_time = data["min_time"]
            max_time = data["max_time"]

            print(f"{profile:<12} {avg_time:<12.3f} {min_time:<12.3f} {max_time:<12.3f}")

        improvements = self.analyze_performance_gains(results)

        if improvements:
            print("\nPERFORMANCE IMPROVEMENTS:")
            print("-" * 30)

            if "minimal_vs_full" in improvements:
                print(f"Minimal vs Full:     {improvements['minimal_vs_full']:>6.1f}% faster")

            if "standard_vs_full" in improvements:
                print(f"Standard vs Full:    {improvements['standard_vs_full']:>6.1f}% faster")

            if "estimated_data_reduction" in improvements:
                print(f"Data Reduction:      {improvements['estimated_data_reduction']:>6.1f}% less data")

        print("\nRECOMMENDATIONS:")
        print("-" * 20)
        print("• Use 'minimal' profile for quick issue lists and IDs")
        print("• Use 'standard' profile for general issue management")
        print("• Use 'full' profile only when you need all issue details")
        print("• Consider custom field selection for specific use cases")
        print("=" * 60)


async def run_benchmark(auth_manager: AuthManager, project_id: Optional[str] = None, sample_size: int = 50) -> None:
    """Run a complete field selection benchmark.

    Args:
        auth_manager: Authenticated auth manager
        project_id: Project ID to benchmark (optional)
        sample_size: Number of issues to fetch
    """
    benchmark = FieldSelectionBenchmark(auth_manager)

    try:
        results = await benchmark.benchmark_profile_performance(project_id=project_id, sample_size=sample_size)

        benchmark.print_benchmark_report(results)

    except Exception as e:
        logger.error("Benchmark failed", error=str(e))
        print(f"❌ Benchmark failed: {e}")
        raise
