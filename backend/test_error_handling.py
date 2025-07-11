#!/usr/bin/env python3
"""
Comprehensive test suite for error handling and retry logic.

This script tests various error scenarios to verify that our error handling
system works correctly across different failure modes.
"""

import os
import sys
import time
import asyncio
import logging
import requests
from typing import Dict, Any, List

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.exceptions import (
    APIException,
    FALAPIException, 
    FileValidationException,
    NetworkException,
    ProcessingException,
    RateLimitException,
    log_exception,
    create_error_response
)
from app.workers.tasks import (
    process_single_image_with_retry,
    process_batch_with_enhanced_retry
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorHandlingTester:
    """Test suite for error handling functionality."""
    
    def __init__(self):
        self.test_results = []
        self.base_url = "http://localhost:8000"
        
    def run_all_tests(self):
        """Run all error handling tests."""
        logger.info("Starting comprehensive error handling tests...")
        
        # Test custom exceptions
        self.test_custom_exceptions()
        
        # Test API error responses
        self.test_api_error_responses()
        
        # Test file validation errors
        self.test_file_validation_errors()
        
        # Test network error scenarios
        self.test_network_errors()
        
        # Test rate limiting scenarios
        self.test_rate_limiting()
        
        # Test backend endpoints
        self.test_backend_endpoints()
        
        # Summary
        self.print_test_summary()
        
    def test_custom_exceptions(self):
        """Test custom exception classes."""
        logger.info("Testing custom exception classes...")
        
        try:
            # Test APIException
            api_error = APIException(
                message="Test API error",
                status_code=400,
                error_code="TEST_ERROR",
                details={"test": "data"}
            )
            
            error_dict = api_error.to_dict()
            assert error_dict["error"] == True
            assert error_dict["status_code"] == 400
            assert error_dict["error_code"] == "TEST_ERROR"
            
            self.test_results.append(("APIException creation and serialization", "PASS"))
            
        except Exception as e:
            self.test_results.append(("APIException creation and serialization", f"FAIL: {e}"))
            
        try:
            # Test FALAPIException
            fal_error = FALAPIException(
                message="FAL API rate limited",
                status_code=429,
                is_rate_limited=True,
                details={"retry_after": 60}
            )
            
            assert fal_error.is_rate_limited == True
            assert fal_error.error_code == "FAL_API_RATE_LIMITED"
            
            self.test_results.append(("FALAPIException with rate limiting", "PASS"))
            
        except Exception as e:
            self.test_results.append(("FALAPIException with rate limiting", f"FAIL: {e}"))
            
        try:
            # Test FileValidationException
            file_error = FileValidationException(
                message="Invalid file type",
                filename="test.txt",
                file_size=1024
            )
            
            assert file_error.filename == "test.txt"
            assert file_error.status_code == 400
            
            self.test_results.append(("FileValidationException", "PASS"))
            
        except Exception as e:
            self.test_results.append(("FileValidationException", f"FAIL: {e}"))
            
    def test_api_error_responses(self):
        """Test API error response formatting."""
        logger.info("Testing API error response formatting...")
        
        try:
            error = ProcessingException(
                message="Processing failed",
                job_id="test-123",
                stage="generation"
            )
            
            response = create_error_response(error)
            assert response["error"] == True
            assert response["error_code"] == "PROCESSING_ERROR"
            assert "job_id" in response["details"]
            
            self.test_results.append(("Error response formatting", "PASS"))
            
        except Exception as e:
            self.test_results.append(("Error response formatting", f"FAIL: {e}"))
            
    def test_file_validation_errors(self):
        """Test file validation error scenarios."""
        logger.info("Testing file validation scenarios...")
        
        # Test cases for different validation failures
        test_cases = [
            {
                "description": "Empty filename",
                "filename": "",
                "expected_error": "No filename provided"
            },
            {
                "description": "Invalid file extension",
                "filename": "test.txt",
                "expected_error": "not allowed"
            },
            {
                "description": "Missing file",
                "filename": None,
                "expected_error": "No filename provided"
            }
        ]
        
        for case in test_cases:
            try:
                # Simulate file validation
                if not case["filename"]:
                    raise FileValidationException("No filename provided")
                elif not case["filename"].lower().endswith(('.jpg', '.jpeg', '.png')):
                    raise FileValidationException(f"File extension not allowed: {case['filename']}")
                    
                self.test_results.append((f"File validation: {case['description']}", "PASS"))
                
            except FileValidationException as e:
                if case["expected_error"] in str(e):
                    self.test_results.append((f"File validation: {case['description']}", "PASS"))
                else:
                    self.test_results.append((f"File validation: {case['description']}", f"FAIL: Wrong error message"))
            except Exception as e:
                self.test_results.append((f"File validation: {case['description']}", f"FAIL: {e}"))
                
    def test_network_errors(self):
        """Test network error scenarios."""
        logger.info("Testing network error scenarios...")
        
        try:
            # Test connection timeout
            try:
                response = requests.get("http://10.255.255.1", timeout=1)
            except requests.exceptions.ConnectTimeout:
                network_error = NetworkException(
                    message="Connection timeout",
                    service="test-service",
                    retry_after=30
                )
                assert network_error.retry_after == 30
                self.test_results.append(("Network timeout handling", "PASS"))
            except Exception as e:
                self.test_results.append(("Network timeout handling", f"FAIL: {e}"))
                
        except Exception as e:
            self.test_results.append(("Network error testing", f"FAIL: {e}"))
            
    def test_rate_limiting(self):
        """Test rate limiting scenarios."""
        logger.info("Testing rate limiting scenarios...")
        
        try:
            # Test rate limit exception
            rate_limit_error = RateLimitException(
                message="Rate limit exceeded",
                retry_after=120,
                limit_type="api_requests"
            )
            
            assert rate_limit_error.retry_after == 120
            assert rate_limit_error.status_code == 429
            
            self.test_results.append(("Rate limit exception", "PASS"))
            
        except Exception as e:
            self.test_results.append(("Rate limit exception", f"FAIL: {e}"))
            
    def test_backend_endpoints(self):
        """Test backend endpoint error handling."""
        logger.info("Testing backend endpoint error handling...")
        
        # Test invalid file upload
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/upload",
                files=[("files", ("test.txt", "invalid content", "text/plain"))],
                timeout=10
            )
            
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get("error") == True:
                    self.test_results.append(("Backend file validation", "PASS"))
                else:
                    self.test_results.append(("Backend file validation", "FAIL: Wrong response format"))
            else:
                self.test_results.append(("Backend file validation", f"FAIL: Wrong status code {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            self.test_results.append(("Backend file validation", "SKIP: Backend not running"))
        except Exception as e:
            self.test_results.append(("Backend file validation", f"FAIL: {e}"))
            
        # Test invalid task ID
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/status/tasks/invalid-task-id/status",
                timeout=10
            )
            
            if response.status_code == 400:
                self.test_results.append(("Backend task validation", "PASS"))
            else:
                self.test_results.append(("Backend task validation", f"FAIL: Wrong status code {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            self.test_results.append(("Backend task validation", "SKIP: Backend not running"))
        except Exception as e:
            self.test_results.append(("Backend task validation", f"FAIL: {e}"))
            
    def print_test_summary(self):
        """Print test results summary."""
        logger.info("Test Results Summary:")
        logger.info("=" * 60)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, result in self.test_results:
            if result == "PASS":
                passed += 1
                status = "✓"
            elif result.startswith("SKIP"):
                skipped += 1
                status = "~"
            else:
                failed += 1
                status = "✗"
                
            logger.info(f"{status} {test_name}: {result}")
            
        logger.info("=" * 60)
        logger.info(f"Total: {len(self.test_results)}, Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
        
        if failed > 0:
            logger.error("Some tests failed! Please review the error handling implementation.")
            return False
        else:
            logger.info("All tests passed! Error handling system is working correctly.")
            return True

def simulate_error_scenarios():
    """Simulate various error scenarios to test recovery mechanisms."""
    logger.info("Simulating error scenarios...")
    
    # Simulate FAL.AI rate limiting
    logger.info("Simulating FAL.AI rate limiting...")
    try:
        fal_error = FALAPIException(
            message="Rate limit exceeded",
            status_code=429,
            is_rate_limited=True
        )
        log_exception(fal_error, "simulation")
    except Exception as e:
        logger.error(f"Error in rate limit simulation: {e}")
        
    # Simulate network timeout
    logger.info("Simulating network timeout...")
    try:
        network_error = NetworkException(
            message="Request timeout",
            service="FAL.AI",
            retry_after=30
        )
        log_exception(network_error, "simulation")
    except Exception as e:
        logger.error(f"Error in timeout simulation: {e}")
        
    # Simulate file validation error
    logger.info("Simulating file validation error...")
    try:
        file_error = FileValidationException(
            message="File too large",
            filename="large_file.jpg",
            file_size=50 * 1024 * 1024  # 50MB
        )
        log_exception(file_error, "simulation")
    except Exception as e:
        logger.error(f"Error in file validation simulation: {e}")

def main():
    """Main test runner."""
    print("Image2Model Error Handling Test Suite")
    print("=" * 50)
    
    # Run error handling tests
    tester = ErrorHandlingTester()
    success = tester.run_all_tests()
    
    # Run error scenario simulations
    simulate_error_scenarios()
    
    print("\nError handling tests completed!")
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()