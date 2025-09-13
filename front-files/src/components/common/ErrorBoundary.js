// src/components/common/ErrorBoundary.js
import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Generate a unique error ID for tracking
    const eventId = Date.now().toString(36) + Math.random().toString(36).substr(2);
    
    this.setState({
      error,
      errorInfo,
      eventId
    });

    // In production, you would send this to your error tracking service
    // e.g., Sentry, LogRocket, etc.
    this.logErrorToService(error, errorInfo, eventId);
  }

  logErrorToService = (error, errorInfo, eventId) => {
    // Mock error logging - replace with your actual error service
    const errorData = {
      eventId,
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    // In development, just log to console
    if (process.env.NODE_ENV === 'development') {
      console.group('🚨 Error Boundary Report');
      console.error('Error:', error);
      console.error('Error Info:', errorInfo);
      console.table(errorData);
      console.groupEnd();
    } else {
      // In production, send to error tracking service
      // fetch('/api/errors', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(errorData)
      // }).catch(err => console.error('Failed to log error:', err));
    }
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null
    });
  };

  render() {
    if (this.state.hasError) {
      const { error, eventId } = this.state;
      const { fallback: Fallback, showDetails = false } = this.props;

      // If a custom fallback component is provided, use it
      if (Fallback) {
        return (
          <Fallback 
            error={error}
            eventId={eventId}
            onRetry={this.handleRetry}
            onReload={this.handleReload}
          />
        );
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
            </div>

            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Algo salió mal
            </h1>
            
            <p className="text-gray-600 mb-6">
              Lo sentimos, ocurrió un error inesperado. Por favor intenta nuevamente.
            </p>

            {eventId && (
              <div className="bg-gray-50 rounded-lg p-3 mb-6">
                <p className="text-xs text-gray-500 mb-1">ID del Error:</p>
                <code className="text-xs bg-gray-200 px-2 py-1 rounded font-mono">
                  {eventId}
                </code>
              </div>
            )}

            {showDetails && error && (
              <details className="text-left mb-6">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                  Detalles técnicos
                </summary>
                <div className="bg-red-50 border border-red-200 rounded p-3">
                  <pre className="text-xs text-red-800 overflow-auto max-h-32">
                    {error.message}
                  </pre>
                </div>
              </details>
            )}

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={this.handleRetry}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Intentar nuevamente
              </button>
              
              <button
                onClick={this.handleGoHome}
                className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                Ir al inicio
              </button>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                Si el problema persiste, contacta al soporte técnico.
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;