// src/utils/storage.js
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  SESSION_EXPIRY: 'session_expiry'
};

export const storage = {
  // Token management
  getAccessToken: () => {
    try {
      return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    } catch (error) {
      console.error('Error reading access token:', error);
      return null;
    }
  },

  setAccessToken: (token) => {
    try {
      if (token) {
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token);
      } else {
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      }
    } catch (error) {
      console.error('Error setting access token:', error);
    }
  },

  getRefreshToken: () => {
    try {
      return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    } catch (error) {
      console.error('Error reading refresh token:', error);
      return null;
    }
  },

  setRefreshToken: (token) => {
    try {
      if (token) {
        localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, token);
      } else {
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      }
    } catch (error) {
      console.error('Error setting refresh token:', error);
    }
  },

  // User data management
  getUserData: () => {
    try {
      const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error reading user data:', error);
      return null;
    }
  },

  setUserData: (userData) => {
    try {
      if (userData) {
        localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
      } else {
        localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      }
    } catch (error) {
      console.error('Error setting user data:', error);
    }
  },

  // Session management
  getSessionExpiry: () => {
    try {
      const expiry = localStorage.getItem(STORAGE_KEYS.SESSION_EXPIRY);
      return expiry ? new Date(expiry) : null;
    } catch (error) {
      console.error('Error reading session expiry:', error);
      return null;
    }
  },

  setSessionExpiry: (expiryDate) => {
    try {
      if (expiryDate) {
        localStorage.setItem(STORAGE_KEYS.SESSION_EXPIRY, expiryDate.toISOString());
      } else {
        localStorage.removeItem(STORAGE_KEYS.SESSION_EXPIRY);
      }
    } catch (error) {
      console.error('Error setting session expiry:', error);
    }
  },

  // Check if session is expired
  isSessionExpired: () => {
    const expiry = storage.getSessionExpiry();
    if (!expiry) return true;
    return new Date() > expiry;
  },

  // Clear all auth data
  clearAuth: () => {
    try {
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      localStorage.removeItem(STORAGE_KEYS.SESSION_EXPIRY);
    } catch (error) {
      console.error('Error clearing auth data:', error);
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    const token = storage.getAccessToken();
    const userData = storage.getUserData();
    const isExpired = storage.isSessionExpired();
    
    return !!(token && userData && !isExpired);
  }
};