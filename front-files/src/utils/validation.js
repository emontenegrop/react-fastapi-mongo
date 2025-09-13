// src/utils/validation.js
import * as Yup from 'yup';

// Common validation patterns
const patterns = {
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  phone: /^[\+]?[1-9][\d]{0,15}$/,
  alphanumeric: /^[a-zA-Z0-9]+$/,
  noXSS: /^[^<>'"&]*$/ // Basic XSS prevention
};

// Custom validation messages
const messages = {
  required: 'Este campo es requerido',
  email: 'Ingrese un email válido',
  password: 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial',
  passwordMatch: 'Las contraseñas no coinciden',
  minLength: (min) => `Debe tener al menos ${min} caracteres`,
  maxLength: (max) => `No debe exceder ${max} caracteres`,
  phone: 'Ingrese un número de teléfono válido',
  noXSS: 'No se permiten caracteres especiales peligrosos'
};

// Sanitization functions
export const sanitize = {
  text: (value) => {
    if (!value) return '';
    return value.toString().trim().replace(/[<>'"&]/g, '');
  },
  
  email: (value) => {
    if (!value) return '';
    return value.toString().trim().toLowerCase();
  },
  
  phone: (value) => {
    if (!value) return '';
    return value.toString().replace(/[^\d+]/g, '');
  },
  
  alphanumeric: (value) => {
    if (!value) return '';
    return value.toString().replace(/[^a-zA-Z0-9]/g, '');
  }
};

// Validation schemas
export const validationSchemas = {
  // Login form validation
  login: Yup.object().shape({
    email: Yup.string()
      .required(messages.required)
      .matches(patterns.email, messages.email)
      .transform(sanitize.email),
    
    password: Yup.string()
      .required(messages.required)
      .min(6, messages.minLength(6))
  }),

  // Enhanced password validation for registration/reset
  password: Yup.object().shape({
    password: Yup.string()
      .required(messages.required)
      .matches(patterns.password, messages.password),
    
    confirmPassword: Yup.string()
      .required(messages.required)
      .oneOf([Yup.ref('password'), null], messages.passwordMatch)
  }),

  // Forgot password validation
  forgotPassword: Yup.object().shape({
    email: Yup.string()
      .required(messages.required)
      .matches(patterns.email, messages.email)
      .transform(sanitize.email)
  }),

  // Reset password validation
  resetPassword: Yup.object().shape({
    token: Yup.string()
      .required(messages.required)
      .min(32, 'Token inválido'),
    
    password: Yup.string()
      .required(messages.required)
      .matches(patterns.password, messages.password),
    
    confirmPassword: Yup.string()
      .required(messages.required)
      .oneOf([Yup.ref('password'), null], messages.passwordMatch)
  }),

  // User profile validation
  profile: Yup.object().shape({
    firstName: Yup.string()
      .required(messages.required)
      .min(2, messages.minLength(2))
      .max(50, messages.maxLength(50))
      .matches(patterns.noXSS, messages.noXSS)
      .transform(sanitize.text),
    
    lastName: Yup.string()
      .required(messages.required)
      .min(2, messages.minLength(2))
      .max(50, messages.maxLength(50))
      .matches(patterns.noXSS, messages.noXSS)
      .transform(sanitize.text),
    
    email: Yup.string()
      .required(messages.required)
      .matches(patterns.email, messages.email)
      .transform(sanitize.email),
    
    phone: Yup.string()
      .nullable()
      .matches(patterns.phone, messages.phone)
      .transform(sanitize.phone)
  }),

  // File upload validation
  fileUpload: Yup.object().shape({
    file: Yup.mixed()
      .required('Seleccione un archivo')
      .test('fileSize', 'El archivo es muy grande (máximo 10MB)', (value) => {
        if (!value) return true;
        return value.size <= 10 * 1024 * 1024; // 10MB
      })
      .test('fileType', 'Tipo de archivo no permitido', (value) => {
        if (!value) return true;
        const allowedTypes = [
          'image/jpeg',
          'image/png',
          'image/gif',
          'application/pdf',
          'application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];
        return allowedTypes.includes(value.type);
      }),
    
    description: Yup.string()
      .max(500, messages.maxLength(500))
      .matches(patterns.noXSS, messages.noXSS)
      .transform(sanitize.text)
  })
};

// Rate limiting helpers
export const rateLimiter = {
  attempts: new Map(),
  
  isBlocked: (key, maxAttempts = 5, windowMs = 15 * 60 * 1000) => {
    const now = Date.now();
    const attempts = rateLimiter.attempts.get(key) || [];
    
    // Remove old attempts outside the time window
    const recentAttempts = attempts.filter(time => now - time < windowMs);
    
    rateLimiter.attempts.set(key, recentAttempts);
    
    return recentAttempts.length >= maxAttempts;
  },
  
  recordAttempt: (key) => {
    const now = Date.now();
    const attempts = rateLimiter.attempts.get(key) || [];
    attempts.push(now);
    rateLimiter.attempts.set(key, attempts);
  },
  
  getRemainingTime: (key, windowMs = 15 * 60 * 1000) => {
    const attempts = rateLimiter.attempts.get(key) || [];
    if (attempts.length === 0) return 0;
    
    const oldestAttempt = Math.min(...attempts);
    const elapsed = Date.now() - oldestAttempt;
    
    return Math.max(0, windowMs - elapsed);
  }
};

// Security validation helpers
export const security = {
  // Check for common SQL injection patterns
  hasSQLInjection: (value) => {
    if (!value) return false;
    const sqlPatterns = [
      /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)/i,
      /(--|\*\/|\/\*)/,
      /['";\x00\x1a]/
    ];
    
    return sqlPatterns.some(pattern => pattern.test(value));
  },
  
  // Check for XSS patterns
  hasXSS: (value) => {
    if (!value) return false;
    const xssPatterns = [
      /<script[^>]*>.*?<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /<iframe/gi,
      /<object/gi,
      /<embed/gi
    ];
    
    return xssPatterns.some(pattern => pattern.test(value));
  },
  
  // Check for path traversal
  hasPathTraversal: (value) => {
    if (!value) return false;
    return /\.\.\/|\.\.\\/.test(value);
  },
  
  // Comprehensive security check
  isSecure: (value) => {
    return !security.hasSQLInjection(value) && 
           !security.hasXSS(value) && 
           !security.hasPathTraversal(value);
  }
};

// Form validation wrapper
export const validateForm = async (schema, values) => {
  try {
    // Security checks
    for (const [key, value] of Object.entries(values)) {
      if (typeof value === 'string' && !security.isSecure(value)) {
        throw new Error(`Contenido no válido detectado en ${key}`);
      }
    }
    
    // Schema validation
    const validatedValues = await schema.validate(values, {
      abortEarly: false,
      stripUnknown: true
    });
    
    return { success: true, data: validatedValues };
  } catch (error) {
    if (error.inner) {
      // Yup validation errors
      const errors = error.inner.reduce((acc, err) => {
        acc[err.path] = err.message;
        return acc;
      }, {});
      
      return { success: false, errors };
    }
    
    // Security or other errors
    return { success: false, error: error.message };
  }
};