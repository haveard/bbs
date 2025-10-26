#!/usr/bin/env python3
"""
Test runner script for the BBS project.
Provides convenient commands for running different types of tests.
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n🏃 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
    else:
        print(f"❌ {description} - FAILED")
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description='BBS Test Runner')
    parser.add_argument('test_type', nargs='?', default='all',
                       choices=['all', 'unit', 'database', 'docker', 'performance', 'fast'],
                       help='Type of tests to run')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--coverage', action='store_true',
                       help='Run with coverage report')
    
    args = parser.parse_args()
    
    # Base command
    base_cmd = ['uv', 'run', 'pytest']
    
    if args.verbose:
        base_cmd.append('-v')
    
    if args.coverage:
        base_cmd.extend(['--cov=bbs_server', '--cov-report=term-missing'])
    
    success = True
    
    if args.test_type == 'all':
        print("🧪 Running all tests...")
        
        # Run unit tests
        cmd = base_cmd + ['tests/test_database.py']
        success &= run_command(cmd, "Database Unit Tests")
        
        # Run Docker integration tests
        cmd = base_cmd + ['tests/test_docker_integration.py']
        success &= run_command(cmd, "Docker Integration Tests")
        
    elif args.test_type == 'unit' or args.test_type == 'database':
        cmd = base_cmd + ['tests/test_database.py']
        success &= run_command(cmd, "Database Unit Tests")
        
    elif args.test_type == 'docker':
        cmd = base_cmd + ['tests/test_docker_integration.py']
        success &= run_command(cmd, "Docker Integration Tests")
        
    elif args.test_type == 'performance':
        cmd = base_cmd + ['tests/test_performance.py', '-m', 'performance']
        success &= run_command(cmd, "Performance Tests")
        
    elif args.test_type == 'fast':
        cmd = base_cmd + ['tests/test_database.py', '-m', 'not slow']
        success &= run_command(cmd, "Fast Unit Tests")
    
    print("\n" + "="*60)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()