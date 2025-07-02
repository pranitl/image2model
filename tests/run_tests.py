#!/usr/bin/env python3
"""
Test runner for Image2Model integration and end-to-end tests.

This script provides a comprehensive test runner with different test categories
and configuration options for the Image2Model platform.
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any
import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """Comprehensive test runner for Image2Model."""
    
    def __init__(self):
        self.project_root = project_root
        self.tests_dir = Path(__file__).parent
        self.backend_url = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
        
    def check_services(self) -> Dict[str, bool]:
        """Check if required services are running."""
        services = {
            'backend': False,
            'frontend': False
        }
        
        # Check backend
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            services['backend'] = response.status_code == 200
        except:
            services['backend'] = False
        
        # Check frontend (basic connectivity)
        try:
            response = requests.get(self.frontend_url, timeout=5)
            services['frontend'] = response.status_code in [200, 404]  # 404 is OK for SPA
        except:
            services['frontend'] = False
        
        return services
    
    def run_tests(self, test_categories: List[str], verbose: bool = False, 
                  parallel: bool = False, coverage: bool = False,
                  html_report: bool = False) -> int:
        """Run tests with specified categories."""
        
        # Check services first
        services = self.check_services()
        print(f"Service status: Backend {'✓' if services['backend'] else '✗'}, "
              f"Frontend {'✓' if services['frontend'] else '✗'}")
        
        if not services['backend']:
            print("⚠️  Backend service not available. Some tests will be skipped.")
        
        # Build pytest command
        cmd = ['python', '-m', 'pytest']
        
        # Add test directories based on categories
        test_paths = []
        for category in test_categories:
            if category == 'integration':
                test_paths.append('tests/integration/')
            elif category == 'e2e':
                test_paths.append('tests/e2e/')
            elif category == 'load':
                test_paths.append('tests/load/')
            elif category == 'docker':
                test_paths.extend(['tests/integration/test_docker_deployment.py'])
            elif category == 'smoke':
                test_paths.extend([
                    'tests/e2e/test_production_validation.py::TestProductionSmokeTest'
                ])
            elif category == 'all':
                test_paths.extend(['tests/'])
        
        if not test_paths:
            test_paths = ['tests/']
        
        cmd.extend(test_paths)
        
        # Add pytest options
        if verbose:
            cmd.append('-v')
        else:
            cmd.append('-q')
        
        # Parallel execution
        if parallel:
            cmd.extend(['-n', 'auto'])
        
        # Coverage
        if coverage:
            cmd.extend(['--cov=backend/app', '--cov-report=html', '--cov-report=term-missing'])
        
        # HTML report
        if html_report:
            cmd.extend(['--html=tests/report.html', '--self-contained-html'])
        
        # Test markers
        markers = []
        if 'docker' in test_categories:
            markers.append('docker')
        if 'load' in test_categories:
            markers.append('load')
        if 'e2e' in test_categories:
            markers.append('e2e')
        if 'integration' in test_categories:
            markers.append('integration')
        
        if markers:
            cmd.extend(['-m', ' or '.join(markers)])
        
        # Add common options
        cmd.extend([
            '--tb=short',
            '--strict-markers',
            '--disable-warnings'
        ])
        
        print(f"Running tests: {' '.join(cmd)}")
        print("-" * 80)
        
        # Run tests
        start_time = time.time()
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            elapsed_time = time.time() - start_time
            
            print("-" * 80)
            print(f"Tests completed in {elapsed_time:.2f} seconds")
            
            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed.")
            
            return result.returncode
            
        except KeyboardInterrupt:
            print("\\n❌ Tests interrupted by user")
            return 1
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return 1
    
    def setup_test_environment(self):
        """Set up test environment."""
        print("Setting up test environment...")
        
        # Install test dependencies
        requirements_file = self.tests_dir / 'requirements.txt'
        if requirements_file.exists():
            print("Installing test dependencies...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], check=True)
        
        # Create necessary directories
        (self.tests_dir / 'fixtures' / 'files').mkdir(parents=True, exist_ok=True)
        
        print("✅ Test environment ready")
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("Generating test report...")
        
        # Run all tests with HTML output
        cmd = [
            'python', '-m', 'pytest',
            'tests/',
            '--html=tests/comprehensive_report.html',
            '--self-contained-html',
            '--cov=backend/app',
            '--cov-report=html:tests/coverage_html',
            '--cov-report=xml:tests/coverage.xml',
            '-v'
        ]
        
        subprocess.run(cmd, cwd=self.project_root)
        
        print("✅ Test report generated:")
        print(f"  - HTML Report: tests/comprehensive_report.html")
        print(f"  - Coverage HTML: tests/coverage_html/index.html")
        print(f"  - Coverage XML: tests/coverage.xml")

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Image2Model Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Categories:
  integration    - Integration tests for API endpoints and workflows
  e2e           - End-to-end tests for complete user scenarios
  load          - Load and performance tests
  docker        - Docker deployment and configuration tests
  smoke         - Quick smoke tests for production validation
  all           - All test categories

Examples:
  python tests/run_tests.py smoke                    # Quick smoke tests
  python tests/run_tests.py integration e2e -v      # Integration and E2E tests with verbose output
  python tests/run_tests.py all --parallel --html   # All tests in parallel with HTML report
  python tests/run_tests.py load --coverage         # Load tests with coverage
        """
    )
    
    parser.add_argument(
        'categories',
        nargs='*',
        default=[],
        choices=['integration', 'e2e', 'load', 'docker', 'smoke', 'all'],
        help='Test categories to run (default: smoke)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML test report'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Set up test environment'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive test report'
    )
    
    # Check for special commands first
    if '--setup' in sys.argv:
        runner = TestRunner()
        runner.setup_test_environment()
        return 0
    
    if '--report' in sys.argv:
        runner = TestRunner()
        runner.generate_test_report()
        return 0
    
    args = parser.parse_args()
    runner = TestRunner()
    
    # Run tests
    categories = args.categories if args.categories else ['smoke']
    return runner.run_tests(
        test_categories=categories,
        verbose=args.verbose,
        parallel=args.parallel,
        coverage=args.coverage,
        html_report=args.html
    )

if __name__ == '__main__':
    sys.exit(main())