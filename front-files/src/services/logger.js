// src/services/logger.js
import { logService } from './api';

export class Logger {
  constructor() {
    this.logQueue = [];
    this.isOnline = navigator.onLine;
    this.flushInterval = 5000; // 5 seconds
    this.maxQueueSize = 100;
    
    this.setupEventListeners();
    this.startPeriodicFlush();
  }

  setupEventListeners() {
    // Monitor online/offline status
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.flushLogs();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });

    // Log page visibility changes
    document.addEventListener('visibilitychange', () => {
      this.logEvent('page_visibility', {
        visible: !document.hidden,
        timestamp: new Date().toISOString()
      });
    });

    // Log unhandled errors
    window.addEventListener('error', (event) => {
      this.logError('javascript_error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack
      });
    });

    // Log unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.logError('unhandled_promise_rejection', {
        reason: event.reason,
        promise: event.promise
      });
    });

    // Flush logs before page unload
    window.addEventListener('beforeunload', () => {
      this.flushLogs(true); // Force flush
    });
  }

  startPeriodicFlush() {
    setInterval(() => {
      if (this.logQueue.length > 0 && this.isOnline) {
        this.flushLogs();
      }
    }, this.flushInterval);
  }

  // Add log entry to queue
  addToQueue(logEntry) {
    // Add timestamp and session info
    const enrichedEntry = {
      ...logEntry,
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId(),
      userId: this.getUserId(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      referrer: document.referrer
    };

    this.logQueue.push(enrichedEntry);

    // Prevent queue from growing too large
    if (this.logQueue.length > this.maxQueueSize) {
      this.logQueue = this.logQueue.slice(-this.maxQueueSize);
    }

    // Store in localStorage as backup
    try {
      localStorage.setItem('logQueue', JSON.stringify(this.logQueue));
    } catch (error) {
      console.warn('Failed to store logs in localStorage:', error);
    }
  }

  // Flush logs to server
  async flushLogs(force = false) {
    if (!this.isOnline && !force) return;
    if (this.logQueue.length === 0) return;

    const logsToSend = [...this.logQueue];
    this.logQueue = [];

    try {
      await logService.logEvent({
        logs: logsToSend,
        batchId: Date.now().toString(),
        count: logsToSend.length
      });

      // Clear localStorage backup on successful send
      localStorage.removeItem('logQueue');
    } catch (error) {
      // On error, restore logs to queue
      this.logQueue = [...logsToSend, ...this.logQueue];
      console.warn('Failed to send logs to server:', error);
    }
  }

  // Get or create session ID
  getSessionId() {
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
      sessionId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
  }

  // Get current user ID
  getUserId() {
    try {
      const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
      return userData.id || 'anonymous';
    } catch {
      return 'anonymous';
    }
  }

  // Log different types of events
  logEvent(event, data = {}, level = 'info') {
    this.addToQueue({
      type: 'event',
      level,
      event,
      data
    });
  }

  logError(error, data = {}) {
    const errorData = {
      type: 'error',
      level: 'error',
      error: typeof error === 'string' ? error : error.message,
      data
    };

    if (error.stack) {
      errorData.stack = error.stack;
    }

    this.addToQueue(errorData);
  }

  logWarning(message, data = {}) {
    this.addToQueue({
      type: 'warning',
      level: 'warn',
      message,
      data
    });
  }

  logInfo(message, data = {}) {
    this.addToQueue({
      type: 'info',
      level: 'info',
      message,
      data
    });
  }

  logDebug(message, data = {}) {
    if (process.env.NODE_ENV === 'development') {
      this.addToQueue({
        type: 'debug',
        level: 'debug',
        message,
        data
      });
    }
  }

  // User interaction logging
  logUserAction(action, data = {}) {
    this.logEvent('user_action', {
      action,
      ...data
    });
  }

  logPageView(path = window.location.pathname) {
    this.logEvent('page_view', {
      path,
      search: window.location.search,
      hash: window.location.hash
    });
  }

  logFormSubmission(formName, success = true, errors = []) {
    this.logEvent('form_submission', {
      formName,
      success,
      errors
    });
  }

  logApiCall(method, endpoint, status, responseTime) {
    this.logEvent('api_call', {
      method,
      endpoint,
      status,
      responseTime
    });
  }

  logFileOperation(operation, fileName, fileSize, success = true, error = null) {
    this.logEvent('file_operation', {
      operation,
      fileName,
      fileSize,
      success,
      error
    });
  }

  // Performance logging
  logPerformance(metric, value, context = {}) {
    this.logEvent('performance', {
      metric,
      value,
      context
    });
  }

  logWebVitals(vitals) {
    this.logEvent('web_vitals', vitals);
  }

  // Security logging
  logSecurityEvent(event, severity = 'medium', data = {}) {
    this.addToQueue({
      type: 'security',
      level: 'warn',
      event,
      severity,
      data,
      requiresImmediate: severity === 'high'
    });

    // For high severity events, try to flush immediately
    if (severity === 'high' && this.isOnline) {
      this.flushLogs();
    }
  }

  logAuthEvent(event, success = true, data = {}) {
    this.logSecurityEvent('auth_event', success ? 'low' : 'high', {
      event,
      success,
      ...data
    });
  }

  // Initialize logging on page load
  init() {
    // Restore logs from localStorage if any
    try {
      const storedLogs = localStorage.getItem('logQueue');
      if (storedLogs) {
        this.logQueue = JSON.parse(storedLogs);
      }
    } catch (error) {
      console.warn('Failed to restore logs from localStorage:', error);
    }

    // Log initial page load
    this.logPageView();
    
    // Log performance metrics when available
    if ('performance' in window) {
      window.addEventListener('load', () => {
        setTimeout(() => {
          const navigation = performance.getEntriesByType('navigation')[0];
          if (navigation) {
            this.logPerformance('page_load', navigation.loadEventEnd - navigation.fetchStart);
            this.logPerformance('dom_content_loaded', navigation.domContentLoadedEventEnd - navigation.fetchStart);
          }
        }, 0);
      });
    }

    console.log('Logger initialized');
  }
}

// Create and initialize logger instance
export const logger = new Logger();

// Initialize on import
if (typeof window !== 'undefined') {
  logger.init();
}

export default logger;