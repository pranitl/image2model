/**
 * Error Context Provider for global error state management.
 * 
 * Provides centralized error handling, retry logic, and error recovery
 * across the entire application.
 */

import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react';
import { parseError, handleError as handleErrorUtil, getUserFriendlyMessage, getRetryInfo, APIError, NetworkError, ValidationError } from '../utils/errorHandler';
import { useToast } from '../components/Toast';

export interface ErrorState {
  globalError: Error | null;
  componentErrors: Record<string, Error>;
  retryAttempts: Record<string, number>;
  isRetrying: Record<string, boolean>;
  lastErrorTime: number | null;
}

type ErrorAction = 
  | { type: 'SET_GLOBAL_ERROR'; payload: Error | null }
  | { type: 'SET_COMPONENT_ERROR'; payload: { component: string; error: Error | null } }
  | { type: 'INCREMENT_RETRY'; payload: string }
  | { type: 'SET_RETRYING'; payload: { key: string; isRetrying: boolean } }
  | { type: 'CLEAR_ERRORS' }
  | { type: 'CLEAR_COMPONENT_ERROR'; payload: string };

const initialState: ErrorState = {
  globalError: null,
  componentErrors: {},
  retryAttempts: {},
  isRetrying: {},
  lastErrorTime: null
};

function errorReducer(state: ErrorState, action: ErrorAction): ErrorState {
  switch (action.type) {
    case 'SET_GLOBAL_ERROR':
      return {
        ...state,
        globalError: action.payload,
        lastErrorTime: action.payload ? Date.now() : null
      };

    case 'SET_COMPONENT_ERROR':
      const { component, error } = action.payload;
      const newComponentErrors = { ...state.componentErrors };
      
      if (error) {
        newComponentErrors[component] = error;
      } else {
        delete newComponentErrors[component];
      }

      return {
        ...state,
        componentErrors: newComponentErrors,
        lastErrorTime: error ? Date.now() : state.lastErrorTime
      };

    case 'INCREMENT_RETRY':
      return {
        ...state,
        retryAttempts: {
          ...state.retryAttempts,
          [action.payload]: (state.retryAttempts[action.payload] || 0) + 1
        }
      };

    case 'SET_RETRYING':
      return {
        ...state,
        isRetrying: {
          ...state.isRetrying,
          [action.payload.key]: action.payload.isRetrying
        }
      };

    case 'CLEAR_ERRORS':
      return initialState;

    case 'CLEAR_COMPONENT_ERROR':
      const clearedComponentErrors = { ...state.componentErrors };
      delete clearedComponentErrors[action.payload];
      
      return {
        ...state,
        componentErrors: clearedComponentErrors
      };

    default:
      return state;
  }
}

interface ErrorContextType {
  state: ErrorState;
  setGlobalError: (error: Error | null) => void;
  setComponentError: (component: string, error: Error | null) => void;
  clearErrors: () => void;
  clearComponentError: (component: string) => void;
  handleError: (error: any, component?: string, showToast?: boolean) => void;
  retryOperation: (operationKey: string, operation: () => Promise<any> | any) => Promise<void>;
  getErrorForComponent: (component: string) => Error | null;
  hasErrors: () => boolean;
  canRetry: (operationKey: string, maxRetries?: number) => boolean;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

export function useError() {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
}

interface ErrorProviderProps {
  children: ReactNode;
  maxRetries?: number;
  onError?: (error: Error, component?: string) => void;
}

export function ErrorProvider({ children, maxRetries = 3, onError }: ErrorProviderProps) {
  const [state, dispatch] = useReducer(errorReducer, initialState);
  const { showError, showWarning } = useToast();

  const setGlobalError = useCallback((error: Error | null) => {
    dispatch({ type: 'SET_GLOBAL_ERROR', payload: error });
    
    if (error && onError) {
      onError(error);
    }
  }, [onError]);

  const setComponentError = useCallback((component: string, error: Error | null) => {
    dispatch({ type: 'SET_COMPONENT_ERROR', payload: { component, error } });
    
    if (error && onError) {
      onError(error, component);
    }
  }, [onError]);

  const clearErrors = useCallback(() => {
    dispatch({ type: 'CLEAR_ERRORS' });
  }, []);

  const clearComponentError = useCallback((component: string) => {
    dispatch({ type: 'CLEAR_COMPONENT_ERROR', payload: component });
  }, []);

  const handleError = useCallback((
    error: any, 
    component?: string, 
    showToast: boolean = true
  ) => {
    const { parsedError, userMessage, retryInfo } = handleErrorUtil(error, { 
      component, 
      action: 'handleError' 
    });

    // Set error in appropriate context
    if (component) {
      setComponentError(component, parsedError);
    } else {
      setGlobalError(parsedError);
    }

    // Show toast notification if requested
    if (showToast) {
      if (parsedError instanceof APIError && parsedError.status >= 500) {
        showError(userMessage, {
          title: 'Server Error',
          action: retryInfo.canRetry ? {
            label: 'Retry',
            onClick: () => {
              if (component) {
                clearComponentError(component);
              } else {
                setGlobalError(null);
              }
            }
          } : undefined
        });
      } else if (parsedError instanceof NetworkError) {
        showWarning(userMessage, {
          title: 'Connection Issue',
          action: {
            label: 'Retry',
            onClick: () => {
              if (component) {
                clearComponentError(component);
              } else {
                setGlobalError(null);
              }
            }
          }
        });
      } else if (parsedError instanceof ValidationError) {
        showWarning(userMessage, {
          title: 'Validation Error'
        });
      } else {
        showError(userMessage, {
          title: component ? `${component} Error` : 'Error'
        });
      }
    }
  }, [setGlobalError, setComponentError, clearComponentError, showError, showWarning]);

  const retryOperation = useCallback(async (
    operationKey: string, 
    operation: () => Promise<any> | any
  ) => {
    const currentRetries = state.retryAttempts[operationKey] || 0;
    
    if (currentRetries >= maxRetries) {
      const error = new Error(`Maximum retry attempts (${maxRetries}) exceeded for operation: ${operationKey}`);
      handleError(error, operationKey, true);
      return;
    }

    try {
      dispatch({ type: 'SET_RETRYING', payload: { key: operationKey, isRetrying: true } });
      dispatch({ type: 'INCREMENT_RETRY', payload: operationKey });

      // Clear any existing errors for this operation
      clearComponentError(operationKey);

      const result = await Promise.resolve(operation());
      
      // Success - reset retry count
      dispatch({ type: 'SET_RETRYING', payload: { key: operationKey, isRetrying: false } });
      return result;

    } catch (error) {
      dispatch({ type: 'SET_RETRYING', payload: { key: operationKey, isRetrying: false } });
      
      // Check if this error is retryable
      const retryInfo = getRetryInfo(error);
      
      if (retryInfo.canRetry && currentRetries + 1 < maxRetries) {
        // Schedule retry with delay
        const delay = retryInfo.retryAfter ? retryInfo.retryAfter * 1000 : 1000;
        
        setTimeout(() => {
          retryOperation(operationKey, operation);
        }, delay);
        
        showWarning(`Retry attempt ${currentRetries + 1}/${maxRetries} in ${Math.ceil(delay / 1000)}s`, {
          title: 'Retrying Operation'
        });
      } else {
        // No more retries or not retryable
        handleError(error, operationKey, true);
      }
    }
  }, [state.retryAttempts, maxRetries, handleError, clearComponentError, showWarning]);

  const getErrorForComponent = useCallback((component: string) => {
    return state.componentErrors[component] || null;
  }, [state.componentErrors]);

  const hasErrors = useCallback(() => {
    return state.globalError !== null || Object.keys(state.componentErrors).length > 0;
  }, [state.globalError, state.componentErrors]);

  const canRetry = useCallback((operationKey: string, maxRetriesOverride?: number) => {
    const maxRetriesToUse = maxRetriesOverride || maxRetries;
    const currentRetries = state.retryAttempts[operationKey] || 0;
    return currentRetries < maxRetriesToUse;
  }, [state.retryAttempts, maxRetries]);

  const value: ErrorContextType = {
    state,
    setGlobalError,
    setComponentError,
    clearErrors,
    clearComponentError,
    handleError,
    retryOperation,
    getErrorForComponent,
    hasErrors,
    canRetry
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
}

// Custom hooks for specific error scenarios
export function useComponentError(componentName: string) {
  const { getErrorForComponent, setComponentError, clearComponentError, handleError } = useError();
  
  const error = getErrorForComponent(componentName);
  
  const setError = useCallback((error: Error | null) => {
    setComponentError(componentName, error);
  }, [componentName, setComponentError]);
  
  const clearError = useCallback(() => {
    clearComponentError(componentName);
  }, [componentName, clearComponentError]);
  
  const handleComponentError = useCallback((error: any, showToast: boolean = true) => {
    handleError(error, componentName, showToast);
  }, [componentName, handleError]);
  
  return {
    error,
    setError,
    clearError,
    handleError: handleComponentError,
    hasError: error !== null
  };
}

export function useRetryableOperation(operationKey: string) {
  const { retryOperation, canRetry, state } = useError();
  
  const isRetrying = state.isRetrying[operationKey] || false;
  const retryCount = state.retryAttempts[operationKey] || 0;
  
  const execute = useCallback((operation: () => Promise<any> | any) => {
    return retryOperation(operationKey, operation);
  }, [operationKey, retryOperation]);
  
  return {
    execute,
    isRetrying,
    retryCount,
    canRetry: canRetry(operationKey)
  };
}

// Higher-order component for error handling
export function withErrorHandling<P extends object>(
  Component: React.ComponentType<P>,
  componentName?: string
) {
  const WrappedComponent = (props: P) => {
    const componentKey = componentName || Component.displayName || Component.name || 'UnknownComponent';
    const { handleError } = useComponentError(componentKey);
    
    return (
      <ErrorBoundary
        onError={(error) => handleError(error, false)} // Don't show toast as ErrorBoundary will handle UI
      >
        <Component {...props} />
      </ErrorBoundary>
    );
  };

  WrappedComponent.displayName = `withErrorHandling(${Component.displayName || Component.name})`;
  return WrappedComponent;
}

// Simple error boundary for the HOC
import ErrorBoundary from '../components/ErrorBoundary';

export default ErrorProvider;