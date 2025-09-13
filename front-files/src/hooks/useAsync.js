// src/hooks/useAsync.js
import { useState, useEffect, useCallback, useRef } from 'react';
import { useAppState } from '../contexts/AppStateContext';

export const useAsync = (asyncFunction, dependencies = [], options = {}) => {
  const {
    immediate = true,
    onSuccess,
    onError,
    loadingKey,
    errorKey
  } = options;

  const { actions } = useAppState();
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  });
  
  const mountedRef = useRef(true);
  const pendingPromiseRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async (...params) => {
    // Cancel previous request if still pending
    if (pendingPromiseRef.current) {
      pendingPromiseRef.current.cancel = true;
    }

    const currentPromise = { cancel: false };
    pendingPromiseRef.current = currentPromise;

    setState(prev => ({ ...prev, loading: true, error: null }));
    
    if (loadingKey) {
      actions.setLoading(loadingKey, true);
    }

    if (errorKey) {
      actions.clearError(errorKey);
    }

    try {
      const result = await asyncFunction(...params);
      
      if (!currentPromise.cancel && mountedRef.current) {
        setState({ data: result, loading: false, error: null });
        
        if (onSuccess) {
          onSuccess(result);
        }
      }
      
      return result;
    } catch (error) {
      if (!currentPromise.cancel && mountedRef.current) {
        setState(prev => ({ ...prev, loading: false, error }));
        
        if (errorKey) {
          actions.setError(errorKey, error.message);
        }
        
        if (onError) {
          onError(error);
        }
      }
      
      throw error;
    } finally {
      if (!currentPromise.cancel && mountedRef.current) {
        if (loadingKey) {
          actions.setLoading(loadingKey, false);
        }
      }
      
      if (pendingPromiseRef.current === currentPromise) {
        pendingPromiseRef.current = null;
      }
    }
  }, [asyncFunction, onSuccess, onError, loadingKey, errorKey, actions]);

  // Execute immediately if requested
  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, dependencies);

  return {
    ...state,
    execute,
    reset: () => setState({ data: null, loading: false, error: null })
  };
};

export default useAsync;