/**
 * Toast notification system for displaying error messages and other notifications.
 * 
 * Provides a context-based toast system with auto-dismiss, stacking,
 * and different notification types (error, warning, success, info).
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

export type ToastType = 'error' | 'warning' | 'success' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  dismissible?: boolean;
  persistent?: boolean;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  showError: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => string;
  showWarning: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => string;
  showSuccess: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => string;
  showInfo: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => string;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

interface ToastProviderProps {
  children: React.ReactNode;
  maxToasts?: number;
}

export function ToastProvider({ children, maxToasts = 5 }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newToast: Toast = {
      id,
      duration: 5000,
      dismissible: true,
      persistent: false,
      ...toast
    };

    setToasts(current => {
      const updated = [...current, newToast];
      // Limit the number of toasts
      if (updated.length > maxToasts) {
        return updated.slice(-maxToasts);
      }
      return updated;
    });

    return id;
  }, [maxToasts]);

  const removeToast = useCallback((id: string) => {
    setToasts(current => current.filter(toast => toast.id !== id));
  }, []);

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const showError = useCallback((message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => {
    return addToast({
      type: 'error',
      message,
      duration: 0, // Errors are persistent by default
      ...options
    });
  }, [addToast]);

  const showWarning = useCallback((message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => {
    return addToast({
      type: 'warning',
      message,
      duration: 8000,
      ...options
    });
  }, [addToast]);

  const showSuccess = useCallback((message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => {
    return addToast({
      type: 'success',
      message,
      duration: 4000,
      ...options
    });
  }, [addToast]);

  const showInfo = useCallback((message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => {
    return addToast({
      type: 'info',
      message,
      duration: 5000,
      ...options
    });
  }, [addToast]);

  const value: ToastContextType = {
    toasts,
    addToast,
    removeToast,
    clearToasts,
    showError,
    showWarning,
    showSuccess,
    showInfo
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

function ToastContainer() {
  const { toasts } = useToast();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
}

interface ToastItemProps {
  toast: Toast;
}

function ToastItem({ toast }: ToastItemProps) {
  const { removeToast } = useToast();
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  // Auto-dismiss logic
  useEffect(() => {
    if (toast.duration && toast.duration > 0 && !toast.persistent) {
      const timer = setTimeout(() => {
        handleDismiss();
      }, toast.duration);

      return () => clearTimeout(timer);
    }
  }, [toast.duration, toast.persistent]);

  // Animation logic
  useEffect(() => {
    // Trigger enter animation
    const timer = setTimeout(() => setIsVisible(true), 10);
    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    if (!toast.dismissible) return;

    setIsLeaving(true);
    setTimeout(() => {
      removeToast(toast.id);
    }, 300); // Animation duration
  };

  const getToastStyles = () => {
    const baseStyles = "relative overflow-hidden rounded-lg shadow-lg p-4 transition-all duration-300 transform";
    const visibilityStyles = isVisible && !isLeaving 
      ? "translate-x-0 opacity-100" 
      : "translate-x-full opacity-0";

    switch (toast.type) {
      case 'error':
        return `${baseStyles} ${visibilityStyles} bg-red-50 border border-red-200`;
      case 'warning':
        return `${baseStyles} ${visibilityStyles} bg-yellow-50 border border-yellow-200`;
      case 'success':
        return `${baseStyles} ${visibilityStyles} bg-green-50 border border-green-200`;
      case 'info':
        return `${baseStyles} ${visibilityStyles} bg-blue-50 border border-blue-200`;
      default:
        return `${baseStyles} ${visibilityStyles} bg-gray-50 border border-gray-200`;
    }
  };

  const getIconColor = () => {
    switch (toast.type) {
      case 'error': return 'text-red-600';
      case 'warning': return 'text-yellow-600';
      case 'success': return 'text-green-600';
      case 'info': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getTextColor = () => {
    switch (toast.type) {
      case 'error': return 'text-red-800';
      case 'warning': return 'text-yellow-800';
      case 'success': return 'text-green-800';
      case 'info': return 'text-blue-800';
      default: return 'text-gray-800';
    }
  };

  const renderIcon = () => {
    const iconClass = `w-5 h-5 ${getIconColor()}`;
    
    switch (toast.type) {
      case 'error':
        return (
          <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'warning':
        return (
          <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'success':
        return (
          <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'info':
        return (
          <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className={getToastStyles()}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {renderIcon()}
        </div>
        
        <div className="ml-3 flex-1">
          {toast.title && (
            <h4 className={`text-sm font-medium ${getTextColor()} mb-1`}>
              {toast.title}
            </h4>
          )}
          <p className={`text-sm ${getTextColor()}`}>
            {toast.message}
          </p>
          
          {toast.action && (
            <div className="mt-2">
              <button
                onClick={toast.action.onClick}
                className={`text-xs font-medium underline hover:no-underline ${getTextColor()}`}
              >
                {toast.action.label}
              </button>
            </div>
          )}
        </div>

        {toast.dismissible && (
          <button
            onClick={handleDismiss}
            className={`ml-3 flex-shrink-0 ${getTextColor()} hover:opacity-70 focus:outline-none`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Progress bar for timed toasts */}
      {toast.duration && toast.duration > 0 && !toast.persistent && (
        <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-200">
          <div 
            className={`h-full transition-all linear ${
              toast.type === 'error' ? 'bg-red-400' :
              toast.type === 'warning' ? 'bg-yellow-400' :
              toast.type === 'success' ? 'bg-green-400' :
              'bg-blue-400'
            }`}
            style={{
              animation: `shrink ${toast.duration}ms linear forwards`
            }}
          />
        </div>
      )}

      <style jsx>{`
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  );
}

// Utility hook for error handling with toast notifications
export function useErrorToast() {
  const { showError, showWarning } = useToast();

  const handleError = useCallback((error: any, context?: string) => {
    const message = error.message || 'An unexpected error occurred';
    const title = context ? `${context} Error` : 'Error';
    
    return showError(message, { title });
  }, [showError]);

  const handleWarning = useCallback((message: string, context?: string) => {
    const title = context ? `${context} Warning` : 'Warning';
    
    return showWarning(message, { title });
  }, [showWarning]);

  return { handleError, handleWarning };
}