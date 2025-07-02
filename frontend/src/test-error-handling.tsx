/**
 * Frontend error handling test component.
 * 
 * This component provides a testing interface to verify that our error handling
 * system works correctly in the browser.
 */

import React, { useState } from 'react';
import { useError, useComponentError } from '../contexts/ErrorContext';
import { useToast } from '../components/Toast';
import { useErrorRecovery } from '../hooks/useErrorRecovery';
import {
  APIError,
  NetworkError,
  ValidationError,
  parseError,
  handleError as handleErrorUtil,
  getUserFriendlyMessage
} from '../utils/errorHandler';

const ErrorHandlingTest: React.FC = () => {
  const { handleError: globalHandleError, clearErrors, hasErrors } = useError();
  const { error: componentError, handleError: componentHandleError, clearError } = useComponentError('ErrorHandlingTest');
  const { showError, showWarning, showSuccess, showInfo } = useToast();
  const [testResults, setTestResults] = useState<Array<{ name: string; result: string }>>([]);

  const addTestResult = (name: string, result: string) => {
    setTestResults(prev => [...prev, { name, result }]);
  };

  const clearTestResults = () => {
    setTestResults([]);
  };

  // Error creation tests
  const testAPIError = () => {
    try {
      const error = new APIError(400, 'Bad request', 'VALIDATION_ERROR', { field: 'email' });
      if (error.status === 400 && error.errorCode === 'VALIDATION_ERROR') {
        addTestResult('APIError creation', 'PASS');
      } else {
        addTestResult('APIError creation', 'FAIL');
      }
    } catch (e) {
      addTestResult('APIError creation', `FAIL: ${e}`);
    }
  };

  const testNetworkError = () => {
    try {
      const error = new NetworkError('Connection failed');
      if (error.isRetryable && error.name === 'NetworkError') {
        addTestResult('NetworkError creation', 'PASS');
      } else {
        addTestResult('NetworkError creation', 'FAIL');
      }
    } catch (e) {
      addTestResult('NetworkError creation', `FAIL: ${e}`);
    }
  };

  const testValidationError = () => {
    try {
      const error = new ValidationError('Validation failed', [
        { field: 'email', message: 'Invalid email', type: 'format' }
      ]);
      if (error.validationErrors.length === 1) {
        addTestResult('ValidationError creation', 'PASS');
      } else {
        addTestResult('ValidationError creation', 'FAIL');
      }
    } catch (e) {
      addTestResult('ValidationError creation', `FAIL: ${e}`);
    }
  };

  // Error parsing tests
  const testErrorParsing = () => {
    try {
      // Test API response parsing
      const apiResponse = {
        error: true,
        error_code: 'FILE_VALIDATION_ERROR',
        message: 'File too large',
        status_code: 400,
        details: { max_size: '10MB' }
      };

      const parsedError = parseError({ response: { data: apiResponse } });
      if (parsedError instanceof APIError && parsedError.errorCode === 'FILE_VALIDATION_ERROR') {
        addTestResult('Error parsing (API response)', 'PASS');
      } else {
        addTestResult('Error parsing (API response)', 'FAIL');
      }
    } catch (e) {
      addTestResult('Error parsing (API response)', `FAIL: ${e}`);
    }

    try {
      // Test network error parsing
      const networkError = new Error('fetch failed');
      networkError.name = 'TypeError';
      const parsedError = parseError(networkError);
      if (parsedError instanceof NetworkError) {
        addTestResult('Error parsing (Network error)', 'PASS');
      } else {
        addTestResult('Error parsing (Network error)', 'FAIL');
      }
    } catch (e) {
      addTestResult('Error parsing (Network error)', `FAIL: ${e}`);
    }
  };

  // User message tests
  const testUserMessages = () => {
    try {
      const error = new APIError(413, 'File too large', 'FILE_SIZE_ERROR');
      const message = getUserFriendlyMessage(error);
      if (message.includes('File too large')) {
        addTestResult('User-friendly messages', 'PASS');
      } else {
        addTestResult('User-friendly messages', 'FAIL');
      }
    } catch (e) {
      addTestResult('User-friendly messages', `FAIL: ${e}`);
    }
  };

  // Toast notification tests
  const testToastNotifications = () => {
    try {
      showError('Test error message');
      showWarning('Test warning message');
      showSuccess('Test success message');
      showInfo('Test info message');
      addTestResult('Toast notifications', 'PASS');
    } catch (e) {
      addTestResult('Toast notifications', `FAIL: ${e}`);
    }
  };

  // Error context tests
  const testErrorContext = () => {
    try {
      const testError = new Error('Test component error');
      componentHandleError(testError, false); // Don't show toast
      
      if (componentError) {
        addTestResult('Error context (set error)', 'PASS');
        clearError();
        addTestResult('Error context (clear error)', componentError ? 'FAIL' : 'PASS');
      } else {
        addTestResult('Error context (set error)', 'FAIL');
      }
    } catch (e) {
      addTestResult('Error context', `FAIL: ${e}`);
    }
  };

  // Error recovery tests
  const testErrorRecovery = () => {
    const errorRecovery = useErrorRecovery(
      async () => {
        // Simulate a failing operation
        throw new Error('Simulated failure');
      },
      {
        maxRetries: 2,
        onRetry: (attempt) => {
          addTestResult(`Error recovery (retry ${attempt})`, 'PASS');
        },
        onFinalFailure: () => {
          addTestResult('Error recovery (final failure)', 'PASS');
        }
      }
    );

    errorRecovery.execute().catch(() => {
      // Expected to fail
    });
  };

  // Simulate different error scenarios
  const simulateAPIError = () => {
    const error = new APIError(500, 'Internal server error', 'INTERNAL_ERROR');
    globalHandleError(error, 'ErrorHandlingTest');
  };

  const simulateNetworkError = () => {
    const error = new NetworkError('Failed to fetch data');
    globalHandleError(error, 'ErrorHandlingTest');
  };

  const simulateValidationError = () => {
    const error = new ValidationError('Form validation failed', [
      { field: 'email', message: 'Email is required', type: 'required' },
      { field: 'password', message: 'Password too short', type: 'minLength' }
    ]);
    globalHandleError(error, 'ErrorHandlingTest');
  };

  const simulateComponentError = () => {
    const error = new Error('Component-specific error');
    componentHandleError(error);
  };

  // Simulate error boundary test
  const [shouldThrow, setShouldThrow] = useState(false);

  if (shouldThrow) {
    throw new Error('Error boundary test error');
  }

  const runAllTests = () => {
    clearTestResults();
    testAPIError();
    testNetworkError();
    testValidationError();
    testErrorParsing();
    testUserMessages();
    testToastNotifications();
    testErrorContext();
    testErrorRecovery();
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Error Handling Test Suite
        </h1>

        {/* Test Controls */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-700">Unit Tests</h3>
            <button
              onClick={runAllTests}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Run All Tests
            </button>
            <button
              onClick={clearTestResults}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Clear Results
            </button>
          </div>

          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-700">Error Simulations</h3>
            <button
              onClick={simulateAPIError}
              className="w-full px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
            >
              API Error
            </button>
            <button
              onClick={simulateNetworkError}
              className="w-full px-3 py-1 bg-orange-600 text-white rounded text-sm hover:bg-orange-700"
            >
              Network Error
            </button>
            <button
              onClick={simulateValidationError}
              className="w-full px-3 py-1 bg-yellow-600 text-white rounded text-sm hover:bg-yellow-700"
            >
              Validation Error
            </button>
            <button
              onClick={simulateComponentError}
              className="w-full px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
            >
              Component Error
            </button>
            <button
              onClick={() => setShouldThrow(true)}
              className="w-full px-3 py-1 bg-pink-600 text-white rounded text-sm hover:bg-pink-700"
            >
              Error Boundary Test
            </button>
          </div>
        </div>

        {/* Error State Display */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Global Error State</h4>
            <p className="text-sm text-gray-600">
              Has Errors: {hasErrors() ? 'Yes' : 'No'}
            </p>
            {hasErrors() && (
              <button
                onClick={clearErrors}
                className="mt-2 px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
              >
                Clear Global Errors
              </button>
            )}
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Component Error State</h4>
            <p className="text-sm text-gray-600">
              Component Error: {componentError ? componentError.message : 'None'}
            </p>
            {componentError && (
              <button
                onClick={clearError}
                className="mt-2 px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
              >
                Clear Component Error
              </button>
            )}
          </div>
        </div>

        {/* Test Results */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Test Results</h3>
          {testResults.length === 0 ? (
            <p className="text-gray-500 text-sm">No test results yet. Run tests to see results.</p>
          ) : (
            <div className="space-y-2">
              {testResults.map((result, index) => (
                <div
                  key={index}
                  className={`flex justify-between items-center p-2 rounded ${
                    result.result === 'PASS'
                      ? 'bg-green-100 text-green-800'
                      : result.result.startsWith('FAIL')
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  <span className="font-medium">{result.name}</span>
                  <span className="text-sm">
                    {result.result === 'PASS' ? '✓' : '✗'} {result.result}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">Instructions</h3>
          <ul className="text-blue-700 text-sm space-y-1">
            <li>• Click "Run All Tests" to execute unit tests for error handling utilities</li>
            <li>• Use error simulation buttons to test error display and recovery</li>
            <li>• Check toast notifications in the top-right corner</li>
            <li>• Monitor error state displays for context management</li>
            <li>• Use browser console to see detailed error logs</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ErrorHandlingTest;