#!/usr/bin/env python3
"""Test runner for YouTrack CLI with support for unit and integration tests."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def run_unit_tests(coverage: bool = False, verbose: bool = False) -> int:
    """Run unit tests only."""
    cmd = ["uv", "run", "pytest", "-m", "unit"]

    if coverage:
        cmd.extend(["--cov=youtrack_cli", "--cov-report=html", "--cov-report=term"])

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "Running unit tests")


def run_integration_tests(verbose: bool = False) -> int:
    """Run integration tests only."""
    # Check for required environment variables
    required_vars = ["YOUTRACK_BASE_URL", "YOUTRACK_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"\n❌ Integration tests require environment variables: {', '.join(missing_vars)}")
        print("\nTo run integration tests, set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=<your_value>")
        print("\nOptional environment variables:")
        print("  export YOUTRACK_TEST_PROJECT=FPU  # Default project for testing")
        print("  export YOUTRACK_USERNAME=<your_username>  # For assignment tests")
        return 1

    cmd = ["uv", "run", "pytest", "-m", "integration"]

    if verbose:
        cmd.append("-v")

    print(f"\n🌐 Running integration tests against: {os.getenv('YOUTRACK_BASE_URL')}")
    print(f"Using test project: {os.getenv('YOUTRACK_TEST_PROJECT', 'FPU')}")

    return run_command(cmd, "Running integration tests")


def run_all_tests(coverage: bool = False, verbose: bool = False) -> int:
    """Run all tests (unit and integration)."""
    # Run unit tests first
    unit_result = run_unit_tests(coverage=coverage, verbose=verbose)

    if unit_result != 0:
        print("\n❌ Unit tests failed. Skipping integration tests.")
        return unit_result

    # Run integration tests
    integration_result = run_integration_tests(verbose=verbose)

    if unit_result == 0 and integration_result == 0:
        print("\n✅ All tests passed!")

    return unit_result or integration_result


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Test runner for YouTrack CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py unit                 # Run only unit tests
  python test_runner.py integration          # Run only integration tests
  python test_runner.py all                  # Run all tests
  python test_runner.py unit --coverage      # Run unit tests with coverage
  python test_runner.py all --verbose        # Run all tests with verbose output

Environment variables for integration tests:
  YOUTRACK_BASE_URL      # Required: YouTrack instance URL
  YOUTRACK_API_KEY       # Required: API token for authentication
  YOUTRACK_TEST_PROJECT  # Optional: Project ID for testing (default: FPU)
  YOUTRACK_USERNAME      # Optional: Username for assignment tests
        """,
    )

    parser.add_argument("test_type", choices=["unit", "integration", "all"], help="Type of tests to run")

    parser.add_argument("--coverage", action="store_true", help="Generate coverage report (unit tests only)")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose test output")

    args = parser.parse_args()

    # Change to the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    if args.test_type == "unit":
        exit_code = run_unit_tests(coverage=args.coverage, verbose=args.verbose)
    elif args.test_type == "integration":
        exit_code = run_integration_tests(verbose=args.verbose)
    elif args.test_type == "all":
        exit_code = run_all_tests(coverage=args.coverage, verbose=args.verbose)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
