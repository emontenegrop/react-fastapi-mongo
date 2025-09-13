// src/hooks/useErrorHandler.js
import { useState, useCallback } from 'react';
import { HTTP_STATUS } from '../config/api';

export const useErrorHandler = () => {
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleError = useCallback((error) => {
    console.error('Error handled:', error);
    
    let errorMessage = 'Ha ocurrido un error inesperado';
    let errorType = 'general';

    if (error?.response) {
      // HTTP error response
      const { status, data } = error.response;
      
      switch (status) {
        case HTTP_STATUS.BAD_REQUEST:
          errorMessage = data?.message || 'Solicitud inválida';
          errorType = 'validation';
          break;
          
        case HTTP_STATUS.UNAUTHORIZED:
          errorMessage = 'Credenciales inválidas o sesión expirada';
          errorType = 'auth';
          break;
          
        case HTTP_STATUS.FORBIDDEN:
          errorMessage = 'No tienes permisos para realizar esta acción';
          errorType = 'permission';
          break;
          
        case HTTP_STATUS.NOT_FOUND:
          errorMessage = 'Recurso no encontrado';
          errorType = 'notFound';
          break;
          
        case HTTP_STATUS.INTERNAL_SERVER_ERROR:
          errorMessage = 'Error interno del servidor. Intenta nuevamente';
          errorType = 'server';
          break;
          
        default:
          errorMessage = data?.message || `Error ${status}`;
          errorType = 'http';
      }
    } else if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network')) {
      errorMessage = 'Error de conexión. Verifica tu internet';
      errorType = 'network';
    } else if (error?.code === 'TIMEOUT') {
      errorMessage = 'La solicitud tardó demasiado. Intenta nuevamente';
      errorType = 'timeout';
    } else if (error?.message) {
      errorMessage = error.message;
    }

    setError({
      message: errorMessage,
      type: errorType,
      original: error,
      timestamp: new Date().toISOString()
    });
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const executeAsync = useCallback(async (asyncFn, options = {}) => {
    const { showLoading = true, onSuccess, onError } = options;
    
    try {
      if (showLoading) setIsLoading(true);
      clearError();
      
      const result = await asyncFn();
      
      if (onSuccess) onSuccess(result);
      return result;
      
    } catch (err) {
      handleError(err);
      if (onError) onError(err);
      throw err;
    } finally {
      if (showLoading) setIsLoading(false);
    }
  }, [handleError, clearError]);

  const retry = useCallback(async (retryFn, maxAttempts = 3, delay = 1000) => {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await retryFn();
      } catch (error) {
        if (attempt === maxAttempts) {
          throw error;
        }
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, delay * attempt));
      }
    }
  }, []);

  return {
    error,
    isLoading,
    handleError,
    clearError,
    executeAsync,
    retry,
    hasError: !!error
  };
};