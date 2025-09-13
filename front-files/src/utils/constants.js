// src/utils/constants.js

// Application constants
export const APP_CONFIG = {
  NAME: 'Front Files',
  VERSION: '1.0.0',
  DESCRIPTION: 'Sistema de gestión de archivos',
  COMPANY: 'EMTechnology'
};

// API Configuration
export const API_ENDPOINTS = {
  AUTH: {
    BASE: '/api/v1/auth',
    LOGIN: '/login',
    LOGOUT: '/logout',
    REFRESH: '/refresh',
    ME: '/me',
    FORGOT_PASSWORD: '/forgot-password',
    RESET_PASSWORD: '/reset-password',
    CHANGE_PASSWORD: '/change-password'
  },
  USERS: {
    BASE: '/api/v1/users',
    PROFILE: '/profile',
    AVATAR: '/avatar'
  },
  FILES: {
    BASE: '/api/v1/files',
    UPLOAD: '/upload',
    DOWNLOAD: '/download',
    DELETE: '/delete',
    SEARCH: '/search'
  },
  LOGS: {
    BASE: '/api/v1/logs',
    SYSTEM: '/system',
    SECURITY: '/security',
    USER: '/user'
  }
};

// UI Constants
export const UI = {
  BREAKPOINTS: {
    SM: 640,
    MD: 768,
    LG: 1024,
    XL: 1280,
    '2XL': 1536
  },
  
  ANIMATION_DURATION: {
    FAST: 150,
    NORMAL: 300,
    SLOW: 500
  },
  
  Z_INDEX: {
    DROPDOWN: 1000,
    MODAL: 1050,
    TOOLTIP: 1070,
    TOAST: 1080
  },
  
  COLORS: {
    PRIMARY: {
      50: '#eff6ff',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      900: '#1e3a8a'
    },
    SUCCESS: {
      50: '#f0fdf4',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d'
    },
    ERROR: {
      50: '#fef2f2',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c'
    },
    WARNING: {
      50: '#fffbeb',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309'
    }
  }
};

// Form validation constants
export const VALIDATION = {
  EMAIL: {
    PATTERN: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    MAX_LENGTH: 254
  },
  
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
  },
  
  NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 50,
    PATTERN: /^[a-zA-ZÀ-ÿ\s]+$/
  },
  
  PHONE: {
    PATTERN: /^[\+]?[1-9][\d]{0,15}$/
  }
};

// File upload constants
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/csv'
  ],
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks for large file uploads
  TIMEOUT: 30000 // 30 seconds
};

// Security constants
export const SECURITY = {
  TOKEN_REFRESH_THRESHOLD: 5 * 60 * 1000, // 5 minutes
  MAX_LOGIN_ATTEMPTS: 5,
  LOCKOUT_DURATION: 15 * 60 * 1000, // 15 minutes
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  CSRF_HEADER: 'X-CSRF-Token',
  
  CONTENT_SECURITY_POLICY: {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
    'font-src': ["'self'", 'https://fonts.gstatic.com'],
    'img-src': ["'self'", 'data:', 'https:'],
    'connect-src': ["'self'"]
  }
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK: 'Error de conexión. Verifique su internet.',
  UNAUTHORIZED: 'Credenciales inválidas o sesión expirada.',
  FORBIDDEN: 'No tiene permisos para realizar esta acción.',
  NOT_FOUND: 'Recurso no encontrado.',
  SERVER_ERROR: 'Error interno del servidor.',
  VALIDATION_ERROR: 'Por favor corrija los errores en el formulario.',
  FILE_TOO_LARGE: 'El archivo es demasiado grande.',
  INVALID_FILE_TYPE: 'Tipo de archivo no permitido.',
  
  // Form specific
  REQUIRED_FIELD: 'Este campo es requerido.',
  INVALID_EMAIL: 'Ingrese un email válido.',
  INVALID_PASSWORD: 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial.',
  PASSWORD_MISMATCH: 'Las contraseñas no coinciden.',
  
  // Security
  SUSPICIOUS_ACTIVITY: 'Actividad sospechosa detectada.',
  SESSION_EXPIRED: 'Su sesión ha expirado.',
  RATE_LIMITED: 'Demasiados intentos. Intente nuevamente más tarde.'
};

// Success messages
export const SUCCESS_MESSAGES = {
  LOGIN: 'Sesión iniciada correctamente.',
  LOGOUT: 'Sesión cerrada correctamente.',
  PASSWORD_RESET_SENT: 'Correo de recuperación enviado.',
  PASSWORD_CHANGED: 'Contraseña actualizada correctamente.',
  PROFILE_UPDATED: 'Perfil actualizado correctamente.',
  FILE_UPLOADED: 'Archivo subido correctamente.',
  FILE_DELETED: 'Archivo eliminado correctamente.',
  SETTINGS_SAVED: 'Configuración guardada correctamente.'
};

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  DASHBOARD: '/dashboard',
  PROFILE: '/profile',
  SETTINGS: '/settings',
  FILES: '/files',
  UPLOAD: '/upload',
  UNAUTHORIZED: '/unauthorized',
  NOT_FOUND: '/404'
};

// Local storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  THEME: 'theme',
  LANGUAGE: 'language',
  LAST_ACTIVITY: 'last_activity',
  PREFERENCES: 'preferences'
};

// Event names for custom events
export const EVENTS = {
  AUTH_STATE_CHANGED: 'authStateChanged',
  SESSION_EXPIRED: 'sessionExpired',
  FILE_UPLOADED: 'fileUploaded',
  THEME_CHANGED: 'themeChanged',
  ERROR_OCCURRED: 'errorOccurred'
};

// User roles and permissions
export const USER_ROLES = {
  ADMIN: 'administrador',
  USER: 'usuario',
  MODERATOR: 'moderador',
  GUEST: 'invitado'
};

export const PERMISSIONS = {
  READ_FILES: 'read:files',
  WRITE_FILES: 'write:files',
  DELETE_FILES: 'delete:files',
  MANAGE_USERS: 'manage:users',
  VIEW_LOGS: 'view:logs',
  ADMIN_PANEL: 'admin:panel'
};