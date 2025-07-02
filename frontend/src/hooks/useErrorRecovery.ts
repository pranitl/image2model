/**
 * Custom hook for handling error recovery and retry logic in React components.
 * 
 * Provides utilities for automatic retry, circuit breaker patterns,
 * and graceful error recovery with user feedback.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useError } from '../contexts/ErrorContext';
import { useToast } from '../components/Toast';
import { isRetryableError, getRetryDelay, APIError, NetworkError } from '../utils/errorHandler';

export interface ErrorRecoveryOptions {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
  exponentialBackoff?: boolean;
  circuitBreakerThreshold?: number;
  onRetry?: (attempt: number, error: Error) => void;
  onSuccess?: () => void;
  onFinalFailure?: (error: Error) => void;
}

export interface ErrorRecoveryState {
  isLoading: boolean;
  error: Error | null;
  retryCount: number;
  isRetrying: boolean;
  canRetry: boolean;
  nextRetryAt: number | null;
  circuitBreakerOpen: boolean;
}

export function useErrorRecovery(
  operation: () => Promise<any>,
  options: ErrorRecoveryOptions = {}
) {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 30000,
    exponentialBackoff = true,
    circuitBreakerThreshold = 5,
    onRetry,
    onSuccess,
    onFinalFailure
  } = options;

  const { handleError } = useError();
  const { showError, showWarning, showInfo } = useToast();

  const [state, setState] = useState<ErrorRecoveryState>({
    isLoading: false,
    error: null,
    retryCount: 0,
    isRetrying: false,
    canRetry: true,
    nextRetryAt: null,
    circuitBreakerOpen: false
  });

  const consecutiveFailuresRef = useRef(0);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastSuccessRef = useRef(Date.now());

  // Circuit breaker logic
  const isCircuitBreakerOpen = consecutiveFailuresRef.current >= circuitBreakerThreshold;

  const execute = useCallback(async () => {
    // Check circuit breaker
    if (isCircuitBreakerOpen) {
      const timeSinceLastSuccess = Date.now() - lastSuccessRef.current;
      const circuitBreakerResetTime = 60000; // 1 minute

      if (timeSinceLastSuccess < circuitBreakerResetTime) {
        const error = new Error('Service temporarily unavailable. Please try again later.');
        handleError(error, 'ErrorRecovery', false);
        showError('Service temporarily unavailable due to repeated failures. Please try again in a few minutes.');
        
        setState(prev => ({ 
          ...prev, 
          error,
          circuitBreakerOpen: true 
        }));
        return;
      } else {
        // Reset circuit breaker
        consecutiveFailuresRef.current = 0;
      }
    }

    setState(prev => ({ 
      ...prev, 
      isLoading: true, 
      error: null,
      circuitBreakerOpen: false
    }));

    try {
      const result = await operation();
      
      // Success - reset failure counters
      consecutiveFailuresRef.current = 0;
      lastSuccessRef.current = Date.now();
      
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: null,
        retryCount: 0,
        canRetry: true,
        nextRetryAt: null
      }));

      if (onSuccess) {
        onSuccess();
      }

      return result;

    } catch (error) {
      consecutiveFailuresRef.current += 1;
      
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: error as Error
      }));

      // Check if we should retry
      const shouldRetry = isRetryableError(error) && state.retryCount < maxRetries;

      if (shouldRetry) {
        await scheduleRetry(error as Error);
      } else {
        // Final failure
        setState(prev => ({ 
          ...prev, 
          canRetry: false
        }));

        if (onFinalFailure) {
          onFinalFailure(error as Error);
        }

        handleError(error, 'ErrorRecovery', true);
      }
    }
  }, [operation, state.retryCount, maxRetries, isCircuitBreakerOpen, handleError, showError, onSuccess, onFinalFailure]);

  const scheduleRetry = useCallback(async (error: Error) => {
    const nextRetryCount = state.retryCount + 1;
    
    // Calculate retry delay
    let delay = baseDelay;
    if (exponentialBackoff) {
      delay = Math.min(baseDelay * Math.pow(2, nextRetryCount - 1), maxDelay);
    }

    // Add jitter to prevent thundering herd
    const jitter = Math.random() * 0.1 * delay;
    delay = Math.round(delay + jitter);

    // Special handling for API errors with retry-after header
    if (error instanceof APIError && error.retryAfter) {
      delay = Math.max(delay, error.retryAfter * 1000);
    }

    const nextRetryAt = Date.now() + delay;

    setState(prev => ({ 
      ...prev, 
      isRetrying: true,
      retryCount: nextRetryCount,
      nextRetryAt
    }));

    if (onRetry) {
      onRetry(nextRetryCount, error);
    }

    // Show retry notification
    const retryMessage = `Retrying in ${Math.ceil(delay / 1000)} seconds (${nextRetryCount}/${maxRetries})`;
    showInfo(retryMessage, { 
      duration: Math.min(delay, 5000),
      title: 'Retry Scheduled' 
    });

    // Clear any existing retry timeout
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }

    // Schedule the retry
    retryTimeoutRef.current = setTimeout(async () => {
      setState(prev => ({ 
        ...prev, 
        isRetrying: false,
        nextRetryAt: null
      }));

      await execute();
    }, delay);

  }, [state.retryCount, baseDelay, exponentialBackoff, maxDelay, maxRetries, onRetry, showInfo, execute]);

  const retry = useCallback(() => {
    if (state.canRetry && !state.isRetrying) {
      setState(prev => ({ 
        ...prev, 
        retryCount: 0,
        canRetry: true,
        error: null,
        circuitBreakerOpen: false
      }));
      
      // Reset circuit breaker on manual retry
      consecutiveFailuresRef.current = Math.max(0, consecutiveFailuresRef.current - 1);
      
      execute();
    }
  }, [state.canRetry, state.isRetrying, execute]);

  const reset = useCallback(() => {
    // Clear any pending retry
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }

    setState({
      isLoading: false,
      error: null,
      retryCount: 0,
      isRetrying: false,
      canRetry: true,
      nextRetryAt: null,
      circuitBreakerOpen: false
    });

    consecutiveFailuresRef.current = 0;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  return {
    ...state,
    execute,
    retry,
    reset,
    timeUntilNextRetry: state.nextRetryAt ? Math.max(0, state.nextRetryAt - Date.now()) : 0
  };
}

// Specialized hook for file upload operations
export function useUploadErrorRecovery(
  uploadOperation: (file: File) => Promise<any>,
  options: ErrorRecoveryOptions = {}
) {
  const [uploadState, setUploadState] = useState<{
    uploadingFiles: Set<string>;
    failedFiles: Map<string, Error>;
    completedFiles: Set<string>;
  }>({
    uploadingFiles: new Set(),
    failedFiles: new Map(),
    completedFiles: new Set()
  });

  const baseErrorRecovery = useErrorRecovery(
    () => Promise.resolve(), // Placeholder, will be replaced per file
    {
      maxRetries: 2, // Fewer retries for uploads
      baseDelay: 2000, // Longer base delay for uploads
      ...options
    }
  );

  const uploadFile = useCallback(async (file: File) => {
    const fileKey = `${file.name}_${file.size}_${file.lastModified}`;
    
    setUploadState(prev => ({
      ...prev,
      uploadingFiles: new Set([...prev.uploadingFiles, fileKey]),
      failedFiles: new Map([...prev.failedFiles].filter(([key]) => key !== fileKey))
    }));

    try {
      const result = await uploadOperation(file);
      
      setUploadState(prev => ({
        ...prev,
        uploadingFiles: new Set([...prev.uploadingFiles].filter(f => f !== fileKey)),
        completedFiles: new Set([...prev.completedFiles, fileKey])
      }));

      return result;

    } catch (error) {
      setUploadState(prev => ({
        ...prev,
        uploadingFiles: new Set([...prev.uploadingFiles].filter(f => f !== fileKey)),
        failedFiles: new Map([...prev.failedFiles, [fileKey, error as Error]])
      }));

      throw error;
    }
  }, [uploadOperation]);

  const retryFailedFile = useCallback((file: File) => {
    const fileKey = `${file.name}_${file.size}_${file.lastModified}`;
    
    setUploadState(prev => ({
      ...prev,
      failedFiles: new Map([...prev.failedFiles].filter(([key]) => key !== fileKey))
    }));

    return uploadFile(file);
  }, [uploadFile]);

  const clearFailedFiles = useCallback(() => {
    setUploadState(prev => ({
      ...prev,
      failedFiles: new Map()
    }));
  }, []);

  const resetUploadState = useCallback(() => {
    setUploadState({
      uploadingFiles: new Set(),
      failedFiles: new Map(),
      completedFiles: new Set()
    });
  }, []);

  return {
    ...baseErrorRecovery,
    uploadFile,
    retryFailedFile,
    clearFailedFiles,
    resetUploadState,
    uploadingFiles: uploadState.uploadingFiles,
    failedFiles: uploadState.failedFiles,
    completedFiles: uploadState.completedFiles,
    hasFailedFiles: uploadState.failedFiles.size > 0,
    hasUploadingFiles: uploadState.uploadingFiles.size > 0
  };
}