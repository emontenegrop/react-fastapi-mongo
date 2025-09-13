// src/contexts/AppStateContext.js
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { storage } from '../utils/storage';

const AppStateContext = createContext();

// Action types
const actionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_THEME: 'SET_THEME',
  SET_LANGUAGE: 'SET_LANGUAGE',
  SET_SIDEBAR_OPEN: 'SET_SIDEBAR_OPEN',
  SET_MOBILE: 'SET_MOBILE',
  SET_NOTIFICATIONS: 'SET_NOTIFICATIONS',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  SET_USER_PREFERENCES: 'SET_USER_PREFERENCES',
  UPDATE_USER_PREFERENCE: 'UPDATE_USER_PREFERENCE'
};

// Initial state
const initialState = {
  loading: {
    global: false,
    auth: false,
    data: false
  },
  error: {
    global: null,
    auth: null,
    data: null
  },
  ui: {
    theme: 'light', // 'light' | 'dark' | 'system'
    language: 'es',
    sidebarOpen: true,
    isMobile: false,
    compactMode: false
  },
  notifications: [],
  userPreferences: {
    autoSave: true,
    showNotifications: true,
    emailNotifications: false,
    darkMode: false,
    compactView: false,
    defaultFileView: 'grid' // 'grid' | 'list'
  }
};

// Reducer
const appStateReducer = (state, action) => {
  switch (action.type) {
    case actionTypes.SET_LOADING:
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.key]: action.payload.value
        }
      };

    case actionTypes.SET_ERROR:
      return {
        ...state,
        error: {
          ...state.error,
          [action.payload.key]: action.payload.value
        }
      };

    case actionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: {
          ...state.error,
          [action.payload]: null
        }
      };

    case actionTypes.SET_THEME:
      return {
        ...state,
        ui: {
          ...state.ui,
          theme: action.payload
        }
      };

    case actionTypes.SET_LANGUAGE:
      return {
        ...state,
        ui: {
          ...state.ui,
          language: action.payload
        }
      };

    case actionTypes.SET_SIDEBAR_OPEN:
      return {
        ...state,
        ui: {
          ...state.ui,
          sidebarOpen: action.payload
        }
      };

    case actionTypes.SET_MOBILE:
      return {
        ...state,
        ui: {
          ...state.ui,
          isMobile: action.payload,
          sidebarOpen: action.payload ? false : state.ui.sidebarOpen
        }
      };

    case actionTypes.SET_NOTIFICATIONS:
      return {
        ...state,
        notifications: action.payload
      };

    case actionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, action.payload]
      };

    case actionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(
          notification => notification.id !== action.payload
        )
      };

    case actionTypes.SET_USER_PREFERENCES:
      return {
        ...state,
        userPreferences: {
          ...state.userPreferences,
          ...action.payload
        }
      };

    case actionTypes.UPDATE_USER_PREFERENCE:
      return {
        ...state,
        userPreferences: {
          ...state.userPreferences,
          [action.payload.key]: action.payload.value
        }
      };

    default:
      return state;
  }
};

// Provider component
export const AppStateProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appStateReducer, initialState);

  // Load saved preferences on mount
  useEffect(() => {
    const loadPreferences = () => {
      try {
        const savedPreferences = localStorage.getItem('userPreferences');
        if (savedPreferences) {
          const preferences = JSON.parse(savedPreferences);
          dispatch({
            type: actionTypes.SET_USER_PREFERENCES,
            payload: preferences
          });
        }

        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
          dispatch({
            type: actionTypes.SET_THEME,
            payload: savedTheme
          });
        }

        const savedLanguage = localStorage.getItem('language');
        if (savedLanguage) {
          dispatch({
            type: actionTypes.SET_LANGUAGE,
            payload: savedLanguage
          });
        }
      } catch (error) {
        console.error('Error loading preferences:', error);
      }
    };

    loadPreferences();
  }, []);

  // Save preferences when they change
  useEffect(() => {
    try {
      localStorage.setItem('userPreferences', JSON.stringify(state.userPreferences));
    } catch (error) {
      console.error('Error saving preferences:', error);
    }
  }, [state.userPreferences]);

  useEffect(() => {
    try {
      localStorage.setItem('theme', state.ui.theme);
    } catch (error) {
      console.error('Error saving theme:', error);
    }
  }, [state.ui.theme]);

  useEffect(() => {
    try {
      localStorage.setItem('language', state.ui.language);
    } catch (error) {
      console.error('Error saving language:', error);
    }
  }, [state.ui.language]);

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < 768;
      if (isMobile !== state.ui.isMobile) {
        dispatch({
          type: actionTypes.SET_MOBILE,
          payload: isMobile
        });
      }
    };

    handleResize(); // Check initial size
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [state.ui.isMobile]);

  // Action creators
  const actions = {
    setLoading: (key, value) => {
      dispatch({
        type: actionTypes.SET_LOADING,
        payload: { key, value }
      });
    },

    setError: (key, value) => {
      dispatch({
        type: actionTypes.SET_ERROR,
        payload: { key, value }
      });
    },

    clearError: (key) => {
      dispatch({
        type: actionTypes.CLEAR_ERROR,
        payload: key
      });
    },

    setTheme: (theme) => {
      dispatch({
        type: actionTypes.SET_THEME,
        payload: theme
      });
      
      // Apply theme to document
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },

    setLanguage: (language) => {
      dispatch({
        type: actionTypes.SET_LANGUAGE,
        payload: language
      });
    },

    setSidebarOpen: (isOpen) => {
      dispatch({
        type: actionTypes.SET_SIDEBAR_OPEN,
        payload: isOpen
      });
    },

    toggleSidebar: () => {
      dispatch({
        type: actionTypes.SET_SIDEBAR_OPEN,
        payload: !state.ui.sidebarOpen
      });
    },

    addNotification: (notification) => {
      const id = Date.now().toString();
      dispatch({
        type: actionTypes.ADD_NOTIFICATION,
        payload: { ...notification, id }
      });
      
      // Auto-remove after duration
      if (notification.duration) {
        setTimeout(() => {
          actions.removeNotification(id);
        }, notification.duration);
      }
      
      return id;
    },

    removeNotification: (id) => {
      dispatch({
        type: actionTypes.REMOVE_NOTIFICATION,
        payload: id
      });
    },

    updateUserPreference: (key, value) => {
      dispatch({
        type: actionTypes.UPDATE_USER_PREFERENCE,
        payload: { key, value }
      });
    },

    setUserPreferences: (preferences) => {
      dispatch({
        type: actionTypes.SET_USER_PREFERENCES,
        payload: preferences
      });
    },

    // Utility actions
    showLoading: (key = 'global') => actions.setLoading(key, true),
    hideLoading: (key = 'global') => actions.setLoading(key, false),
    
    showError: (message, key = 'global') => actions.setError(key, message),
    hideError: (key = 'global') => actions.clearError(key),

    // Bulk state reset
    resetAppState: () => {
      dispatch({ type: 'RESET_STATE' });
    }
  };

  const value = {
    state,
    actions,
    // Computed values
    computed: {
      isLoading: (key) => key ? state.loading[key] : Object.values(state.loading).some(Boolean),
      hasError: (key) => key ? !!state.error[key] : Object.values(state.error).some(Boolean),
      isDarkMode: state.ui.theme === 'dark',
      isMobile: state.ui.isMobile,
      notificationCount: state.notifications.length
    }
  };

  return (
    <AppStateContext.Provider value={value}>
      {children}
    </AppStateContext.Provider>
  );
};

// Hook to use app state
export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within AppStateProvider');
  }
  return context;
};

// Selectors for specific state slices
export const useLoading = (key) => {
  const { state, actions } = useAppState();
  return {
    isLoading: key ? state.loading[key] : false,
    setLoading: (value) => actions.setLoading(key, value),
    showLoading: () => actions.showLoading(key),
    hideLoading: () => actions.hideLoading(key)
  };
};

export const useError = (key) => {
  const { state, actions } = useAppState();
  return {
    error: key ? state.error[key] : null,
    hasError: key ? !!state.error[key] : false,
    setError: (value) => actions.setError(key, value),
    clearError: () => actions.clearError(key)
  };
};

export const useTheme = () => {
  const { state, actions } = useAppState();
  return {
    theme: state.ui.theme,
    isDarkMode: state.ui.theme === 'dark',
    setTheme: actions.setTheme,
    toggleTheme: () => {
      const newTheme = state.ui.theme === 'light' ? 'dark' : 'light';
      actions.setTheme(newTheme);
    }
  };
};

export const useNotifications = () => {
  const { state, actions } = useAppState();
  return {
    notifications: state.notifications,
    addNotification: actions.addNotification,
    removeNotification: actions.removeNotification,
    count: state.notifications.length
  };
};