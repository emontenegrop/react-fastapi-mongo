// src/utils/security.js

// Security configuration and utilities
export const SECURITY_CONFIG = {
  // Password requirements
  PASSWORD: {
    MIN_LENGTH: 8,
    REQUIRE_UPPERCASE: true,
    REQUIRE_LOWERCASE: true,
    REQUIRE_NUMBERS: true,
    REQUIRE_SPECIAL_CHARS: true,
    FORBIDDEN_PATTERNS: [
      'password', '123456', 'qwerty', 'admin', 'letmein',
      'welcome', 'monkey', 'dragon', 'master', 'login'
    ]
  },

  // Session management
  SESSION: {
    TIMEOUT_WARNING: 5 * 60 * 1000, // 5 minutes before expiry
    MAX_IDLE_TIME: 30 * 60 * 1000,  // 30 minutes
    REFRESH_INTERVAL: 10 * 60 * 1000 // 10 minutes
  },

  // Rate limiting
  RATE_LIMIT: {
    LOGIN_ATTEMPTS: 5,
    PASSWORD_RESET_ATTEMPTS: 3,
    WINDOW_MS: 15 * 60 * 1000, // 15 minutes
    BLOCK_DURATION: 30 * 60 * 1000 // 30 minutes
  },

  // Content Security Policy
  CSP: {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
    'font-src': ["'self'", 'https://fonts.gstatic.com'],
    'img-src': ["'self'", 'data:', 'https:'],
    'connect-src': ["'self'", process.env.REACT_APP_API_URL || 'http://localhost:8082']
  }
};

// Security utilities
export const security = {
  // Input sanitization
  sanitizeInput: (input) => {
    if (typeof input !== 'string') return input;
    
    return input
      .replace(/[<>'"&]/g, (char) => {
        const entities = {
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#x27;',
          '&': '&amp;'
        };
        return entities[char];
      })
      .trim();
  },

  // Password strength validation
  validatePasswordStrength: (password) => {
    const config = SECURITY_CONFIG.PASSWORD;
    const errors = [];
    
    if (password.length < config.MIN_LENGTH) {
      errors.push(`La contraseña debe tener al menos ${config.MIN_LENGTH} caracteres`);
    }
    
    if (config.REQUIRE_UPPERCASE && !/[A-Z]/.test(password)) {
      errors.push('La contraseña debe contener al menos una letra mayúscula');
    }
    
    if (config.REQUIRE_LOWERCASE && !/[a-z]/.test(password)) {
      errors.push('La contraseña debe contener al menos una letra minúscula');
    }
    
    if (config.REQUIRE_NUMBERS && !/\d/.test(password)) {
      errors.push('La contraseña debe contener al menos un número');
    }
    
    if (config.REQUIRE_SPECIAL_CHARS && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\?]/.test(password)) {
      errors.push('La contraseña debe contener al menos un carácter especial');
    }
    
    // Check for forbidden patterns
    const lowerPassword = password.toLowerCase();
    for (const pattern of config.FORBIDDEN_PATTERNS) {
      if (lowerPassword.includes(pattern)) {
        errors.push('La contraseña no puede contener patrones comunes o predecibles');
        break;
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      score: calculatePasswordScore(password)
    };
  },

  // Generate secure random string
  generateSecureToken: (length = 32) => {
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  },

  // Hash password on client side (for additional security)
  hashPassword: async (password, salt) => {
    const encoder = new TextEncoder();
    const data = encoder.encode(password + salt);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  },

  // Detect potential security threats
  detectThreats: (input) => {
    const threats = [];
    
    // SQL Injection patterns
    const sqlPatterns = [
      /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)/i,
      /(--|\*\/|\/\*)/,
      /['";\x00\x1a]/
    ];
    
    if (sqlPatterns.some(pattern => pattern.test(input))) {
      threats.push('SQL_INJECTION');
    }
    
    // XSS patterns
    const xssPatterns = [
      /<script[^>]*>.*?<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /<iframe/gi,
      /<object/gi,
      /<embed/gi
    ];
    
    if (xssPatterns.some(pattern => pattern.test(input))) {
      threats.push('XSS');
    }
    
    // Path traversal
    if (/\.\.\/|\.\.\\/.test(input)) {
      threats.push('PATH_TRAVERSAL');
    }
    
    // Command injection
    if (/[;&|`$(){}[\]\\]/.test(input)) {
      threats.push('COMMAND_INJECTION');
    }
    
    return threats;
  },

  // Secure headers for API requests
  getSecureHeaders: () => {
    return {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    };
  },

  // Environment validation
  validateEnvironment: () => {
    const issues = [];
    
    // Check if running on HTTPS in production
    if (process.env.NODE_ENV === 'production' && window.location.protocol !== 'https:') {
      issues.push('Application should use HTTPS in production');
    }
    
    // Check for debug mode in production
    if (process.env.NODE_ENV === 'production' && window.localStorage.getItem('debug')) {
      issues.push('Debug mode should be disabled in production');
    }
    
    // Check for exposed API keys
    if (process.env.REACT_APP_API_KEY && window.location.hostname !== 'localhost') {
      console.warn('API keys should not be exposed in client-side code');
    }
    
    return issues;
  }
};

// Session management utilities
export const sessionManager = {
  // Track user activity
  trackActivity: () => {
    const now = Date.now();
    localStorage.setItem('lastActivity', now.toString());
  },

  // Check if session is expired due to inactivity
  isSessionExpired: () => {
    const lastActivity = localStorage.getItem('lastActivity');
    if (!lastActivity) return true;
    
    const now = Date.now();
    const timeSinceActivity = now - parseInt(lastActivity);
    
    return timeSinceActivity > SECURITY_CONFIG.SESSION.MAX_IDLE_TIME;
  },

  // Get time until session expires
  getTimeUntilExpiry: () => {
    const lastActivity = localStorage.getItem('lastActivity');
    if (!lastActivity) return 0;
    
    const now = Date.now();
    const timeSinceActivity = now - parseInt(lastActivity);
    const remaining = SECURITY_CONFIG.SESSION.MAX_IDLE_TIME - timeSinceActivity;
    
    return Math.max(0, remaining);
  },

  // Initialize session monitoring
  initSessionMonitoring: (onExpiry, onWarning) => {
    // Track user activity
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    
    const updateActivity = () => {
      sessionManager.trackActivity();
    };
    
    events.forEach(event => {
      document.addEventListener(event, updateActivity, true);
    });
    
    // Check session status periodically
    const checkSession = () => {
      if (sessionManager.isSessionExpired()) {
        onExpiry();
        return;
      }
      
      const timeLeft = sessionManager.getTimeUntilExpiry();
      if (timeLeft <= SECURITY_CONFIG.SESSION.TIMEOUT_WARNING) {
        onWarning(timeLeft);
      }
    };
    
    const intervalId = setInterval(checkSession, 30000); // Check every 30 seconds
    
    // Return cleanup function
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity, true);
      });
      clearInterval(intervalId);
    };
  }
};

// Helper function to calculate password score
const calculatePasswordScore = (password) => {
  let score = 0;
  
  // Length bonus
  score += Math.min(password.length * 4, 50);
  
  // Character variety bonus
  if (/[a-z]/.test(password)) score += 5;
  if (/[A-Z]/.test(password)) score += 5;
  if (/\d/.test(password)) score += 5;
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\?]/.test(password)) score += 10;
  
  // Consecutive characters penalty
  for (let i = 0; i < password.length - 2; i++) {
    if (password.charCodeAt(i + 1) === password.charCodeAt(i) + 1 &&
        password.charCodeAt(i + 2) === password.charCodeAt(i) + 2) {
      score -= 5;
    }
  }
  
  // Repeated characters penalty
  const charCount = {};
  for (const char of password) {
    charCount[char] = (charCount[char] || 0) + 1;
  }
  
  for (const count of Object.values(charCount)) {
    if (count > 1) {
      score -= (count - 1) * 2;
    }
  }
  
  return Math.max(0, Math.min(100, score));
};