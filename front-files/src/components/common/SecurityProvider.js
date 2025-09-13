// src/components/common/SecurityProvider.js
import React, { createContext, useContext, useEffect, useState } from 'react';
import { security, sessionManager, SECURITY_CONFIG } from '../../utils/security';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from './Toast';

const SecurityContext = createContext();

export const useSecurity = () => {
  const context = useContext(SecurityContext);
  if (!context) {
    throw new Error('useSecurity must be used within SecurityProvider');
  }
  return context;
};

export const SecurityProvider = ({ children }) => {
  const { isAuthenticated, logout } = useAuth();
  const { toast } = useToast();
  const [sessionWarningShown, setSessionWarningShown] = useState(false);

  useEffect(() => {
    // Validate environment on mount
    const environmentIssues = security.validateEnvironment();
    if (environmentIssues.length > 0 && process.env.NODE_ENV === 'development') {
      console.warn('Security Environment Issues:', environmentIssues);
    }

    // Initialize session monitoring for authenticated users
    if (isAuthenticated) {
      const cleanup = sessionManager.initSessionMonitoring(
        handleSessionExpiry,
        handleSessionWarning
      );

      return cleanup;
    }
  }, [isAuthenticated]);

  const handleSessionExpiry = () => {
    toast.warning('Su sesión ha expirado por inactividad', {
      duration: 5000
    });
    
    setTimeout(() => {
      logout();
    }, 1000);
  };

  const handleSessionWarning = (timeLeft) => {
    if (!sessionWarningShown) {
      const minutes = Math.ceil(timeLeft / 1000 / 60);
      toast.warning(`Su sesión expirará en ${minutes} minutos`, {
        duration: 10000
      });
      setSessionWarningShown(true);
      
      // Reset warning flag after 2 minutes
      setTimeout(() => setSessionWarningShown(false), 2 * 60 * 1000);
    }
  };

  const validateInput = (input, rules = {}) => {
    const {
      allowEmpty = false,
      maxLength = 1000,
      sanitize = true,
      checkThreats = true
    } = rules;

    if (!input && !allowEmpty) {
      return { isValid: false, error: 'Este campo es requerido' };
    }

    if (!input) {
      return { isValid: true, value: '' };
    }

    if (input.length > maxLength) {
      return { 
        isValid: false, 
        error: `El texto no puede exceder ${maxLength} caracteres` 
      };
    }

    if (checkThreats) {
      const threats = security.detectThreats(input);
      if (threats.length > 0) {
        return { 
          isValid: false, 
          error: 'Contenido no permitido detectado',
          threats 
        };
      }
    }

    const value = sanitize ? security.sanitizeInput(input) : input;

    return { isValid: true, value };
  };

  const validatePassword = (password) => {
    return security.validatePasswordStrength(password);
  };

  const generateSecureToken = (length) => {
    return security.generateSecureToken(length);
  };

  const getSecureHeaders = () => {
    return security.getSecureHeaders();
  };

  // CSP violation reporting
  const reportCSPViolation = (violationReport) => {
    console.warn('CSP Violation:', violationReport);
    
    // In production, send to monitoring service
    if (process.env.NODE_ENV === 'production') {
      // fetch('/api/security/csp-violations', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(violationReport)
      // });
    }
  };

  // Initialize CSP violation reporting
  useEffect(() => {
    const handleCSPViolation = (event) => {
      reportCSPViolation({
        blockedURI: event.blockedURI,
        documentURI: event.documentURI,
        originalPolicy: event.originalPolicy,
        referrer: event.referrer,
        violatedDirective: event.violatedDirective,
        timestamp: new Date().toISOString()
      });
    };

    document.addEventListener('securitypolicyviolation', handleCSPViolation);
    
    return () => {
      document.removeEventListener('securitypolicyviolation', handleCSPViolation);
    };
  }, []);

  const value = {
    validateInput,
    validatePassword,
    generateSecureToken,
    getSecureHeaders,
    config: SECURITY_CONFIG,
    sessionManager
  };

  return (
    <SecurityContext.Provider value={value}>
      {children}
    </SecurityContext.Provider>
  );
};