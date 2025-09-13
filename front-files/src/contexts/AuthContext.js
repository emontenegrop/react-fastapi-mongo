// src/contexts/AuthContext.js
import React, { createContext, useState, useEffect, useContext } from "react";
import axiosInstance from "../api/axios";
import { useNavigate } from "react-router-dom";
import { storage } from "../utils/storage";
import { API_CONFIG } from "../config/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Initialize authentication state
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check if user is authenticated and session is valid
      if (storage.isAuthenticated()) {
        const userData = storage.getUserData();
        
        // Validate token with backend
        try {
          const response = await axiosInstance.get(API_CONFIG.ENDPOINTS.AUTH.ME);
          const serverUser = response.data.user;
          
          // Update user data if it differs
          if (JSON.stringify(userData) !== JSON.stringify(serverUser)) {
            storage.setUserData(serverUser);
            setUser(serverUser);
          } else {
            setUser(userData);
          }
        } catch (error) {
          // Token is invalid, clear auth data
          handleAuthError();
        }
      } else {
        // Clear any stale auth data
        storage.clearAuth();
      }
    } catch (error) {
      console.error("Error initializing auth:", error);
      handleAuthError();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      
      // Validate inputs
      if (!email || !password) {
        throw new Error("Email y contraseña son requeridos");
      }

      const response = await axiosInstance.post(API_CONFIG.ENDPOINTS.AUTH.LOGIN, {
        email: email.trim().toLowerCase(),
        password
      });

      const { 
        accessToken, 
        refreshToken, 
        user: userData, 
        expiresIn = 3600 // Default 1 hour
      } = response.data;

      if (!accessToken || !userData) {
        throw new Error("Respuesta inválida del servidor");
      }

      // Store auth data securely
      storage.setAccessToken(accessToken);
      if (refreshToken) {
        storage.setRefreshToken(refreshToken);
      }
      storage.setUserData(userData);
      
      // Set session expiry
      const expiry = new Date();
      expiry.setSeconds(expiry.getSeconds() + expiresIn);
      storage.setSessionExpiry(expiry);

      setUser(userData);
      
      // Navigate to dashboard
      navigate("/dashboard");
      return { success: true };

    } catch (error) {
      const errorMessage = error.response?.data?.message || error.message || "Error de credenciales";
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const logout = async () => {
    try {
      // Try to notify server about logout
      const refreshToken = storage.getRefreshToken();
      if (refreshToken) {
        try {
          await axiosInstance.post(API_CONFIG.ENDPOINTS.AUTH.LOGOUT, {
            refreshToken
          });
        } catch (error) {
          // Server logout failed, but continue with client logout
          console.warn("Server logout failed:", error);
        }
      }
    } catch (error) {
      console.warn("Logout request failed:", error);
    } finally {
      // Always clear client-side auth data
      handleAuthError();
    }
  };

  const handleAuthError = () => {
    storage.clearAuth();
    setUser(null);
    setError(null);
    
    // Only navigate if not already on login page
    if (window.location.pathname !== "/login") {
      navigate("/login");
    }
  };

  const sendPasswordResetEmail = async (email) => {
    try {
      setError(null);
      
      if (!email || !email.trim()) {
        throw new Error("Email es requerido");
      }

      const response = await axiosInstance.post(API_CONFIG.ENDPOINTS.AUTH.FORGOT_PASSWORD, {
        email: email.trim().toLowerCase()
      });

      return response.data;
    } catch (error) {
      const errorMessage = error.response?.data?.message || "Error al enviar el correo de recuperación";
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const resetPassword = async (token, newPassword, confirmPassword) => {
    try {
      setError(null);
      
      if (!token || !newPassword || !confirmPassword) {
        throw new Error("Todos los campos son requeridos");
      }

      if (newPassword !== confirmPassword) {
        throw new Error("Las contraseñas no coinciden");
      }

      if (newPassword.length < 8) {
        throw new Error("La contraseña debe tener al menos 8 caracteres");
      }

      const response = await axiosInstance.post(API_CONFIG.ENDPOINTS.AUTH.RESET_PASSWORD, {
        token,
        password: newPassword
      });

      return response.data;
    } catch (error) {
      const errorMessage = error.response?.data?.message || "Error al restablecer la contraseña";
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const refreshUserData = async () => {
    try {
      const response = await axiosInstance.get(API_CONFIG.ENDPOINTS.AUTH.ME);
      const userData = response.data.user;
      
      storage.setUserData(userData);
      setUser(userData);
      
      return userData;
    } catch (error) {
      console.error("Error refreshing user data:", error);
      handleAuthError();
      throw error;
    }
  };

  const value = {
    user,
    isAuthenticated: !!user && storage.isAuthenticated(),
    loading,
    error,
    login,
    logout,
    sendPasswordResetEmail,
    resetPassword,
    refreshUserData,
    clearError: () => setError(null)
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
