#!/usr/bin/env python3
"""
Script to run tests with coverage reporting.

This script runs all tests and generates a coverage report.
"""

import os
import sys
import subprocess
import argparse


def run_tests_with_coverage(args):
    """Run tests with coverage reporting."""
    # Ensure pytest and pytest-cov are installed
    try:
        import pytest
        import pytest_cov
    except ImportError:
        print("Installing required packages: pytest, pytest-cov")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    # Build the command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add coverage options
    cmd.extend(["--cov=jess", "--cov-report=term", "--cov-report=html"])
    
    # Add verbose flag if requested
    if args.verbose:
        cmd.append("-v")
    
    # Add specific test file if provided
    if args.test_file:
        cmd.append(args.test_file)
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # Print report location
    if result.returncode == 0:
        print("\nHTML coverage report generated in htmlcov/index.html")
    
    return result.returncode


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run tests with coverage reporting")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("test_file", nargs="?", help="Specific test file to run")
    
    args = parser.parse_args()
    
    return run_tests_with_coverage(args)


if __name__ == "__main__":
    sys.exit(main())