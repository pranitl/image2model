/**
 * React Error Boundary component for handling component errors gracefully.
 * 
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { createErrorBoundaryError, logError } from '../utils/errorHandler';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
  errorId: string;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetKeys?: Array<string | number>;
  resetOnPropsChange?: boolean;
  isolate?: boolean; // If true, only catches errors from immediate children
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error
    const boundaryError = createErrorBoundaryError(error, errorInfo);
    logError(boundaryError, {
      component: 'ErrorBoundary',
      action: 'componentDidCatch'
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Update state with error info
    this.setState({
      error,
      errorInfo
    });
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetKeys, resetOnPropsChange } = this.props;
    const { hasError } = this.state;

    // Reset error state if reset keys changed
    if (hasError && resetKeys) {
      const hasResetKeyChanged = resetKeys.some((key, index) => 
        prevProps.resetKeys?.[index] !== key
      );

      if (hasResetKeyChanged) {
        this.resetErrorBoundary();
      }
    }

    // Reset error state if any props changed (when resetOnPropsChange is true)
    if (hasError && resetOnPropsChange) {
      const propsChanged = Object.keys(this.props).some(key => 
        key !== 'children' && 
        key !== 'resetOnPropsChange' && 
        (this.props as any)[key] !== (prevProps as any)[key]
      );

      if (propsChanged) {
        this.resetErrorBoundary();
      }
    }
  }

  resetErrorBoundary = () => {
    // Clear any pending reset timeout
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
      this.resetTimeoutId = null;
    }

    this.setState({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
      errorId: ''
    });
  };

  handleRetry = () => {
    this.resetErrorBoundary();
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    const { hasError, error, errorInfo, errorId } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // Custom fallback UI
      if (fallback) {
        return fallback;
      }

      // Default fallback UI
      return (
        <ErrorFallbackUI
          error={error}
          errorInfo={errorInfo}
          errorId={errorId}
          onRetry={this.handleRetry}
          onReload={this.handleReload}
        />
      );
    }

    return children;
  }
}

interface ErrorFallbackUIProps {
  error?: Error;
  errorInfo?: ErrorInfo;
  errorId: string;
  onRetry: () => void;
  onReload: () => void;
}

const ErrorFallbackUI: React.FC<ErrorFallbackUIProps> = ({ 
  error, 
  errorInfo, 
  errorId, 
  onRetry, 
  onReload 
}) => {
  const [showDetails, setShowDetails] = React.useState(false);

  return (
    <div className="min-h-[400px] flex items-center justify-center p-6 bg-red-50 border border-red-200 rounded-lg">
      <div className="max-w-md w-full text-center">
        {/* Error Icon */}
        <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
          <svg 
            className="w-8 h-8 text-red-600" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" 
            />
          </svg>
        </div>

        {/* Error Message */}
        <h3 className="text-lg font-semibold text-red-800 mb-2">
          Something went wrong
        </h3>
        <p className="text-red-600 mb-6">
          An unexpected error occurred while rendering this component.
        </p>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={onRetry}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
          >
            Try Again
          </button>
          
          <button
            onClick={onReload}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            Reload Page
          </button>

          <button
            onClick={() => setShowDetails(!showDetails)}
            className="w-full px-4 py-2 bg-transparent text-red-600 border border-red-600 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors text-sm"
          >
            {showDetails ? 'Hide Details' : 'Show Details'}
          </button>
        </div>

        {/* Error Details (Collapsible) */}
        {showDetails && (
          <div className="mt-6 p-4 bg-gray-100 rounded-md text-left">
            <div className="text-xs text-gray-600 mb-2">
              Error ID: {errorId}
            </div>
            
            {error && (
              <div className="mb-3">
                <div className="text-sm font-medium text-gray-700 mb-1">Error:</div>
                <div className="text-xs text-gray-600 font-mono bg-white p-2 rounded border">
                  {error.name}: {error.message}
                </div>
              </div>
            )}

            {errorInfo?.componentStack && (
              <div>
                <div className="text-sm font-medium text-gray-700 mb-1">Component Stack:</div>
                <div className="text-xs text-gray-600 font-mono bg-white p-2 rounded border max-h-32 overflow-y-auto">
                  {errorInfo.componentStack}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Help Text */}
        <p className="text-xs text-gray-500 mt-4">
          If this problem persists, please contact support with the error ID above.
        </p>
      </div>
    </div>
  );
};

// Higher-order component for easier usage
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  return WrappedComponent;
}

// Hook for resetting error boundaries
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  const captureError = React.useCallback((error: Error) => {
    setError(error);
  }, []);

  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return { captureError, resetError };
}

export default ErrorBoundary;