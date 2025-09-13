// src/__tests__/utils/security.test.js
import { security, sessionManager, SECURITY_CONFIG } from '../../utils/security';

// Mock localStorage
const localStorageMock = {
  store: {},
  getItem: jest.fn(key => localStorageMock.store[key] || null),
  setItem: jest.fn((key, value) => {
    localStorageMock.store[key] = value.toString();
  }),
  removeItem: jest.fn(key => {
    delete localStorageMock.store[key];
  }),
  clear: jest.fn(() => {
    localStorageMock.store = {};
  })
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('Security Utils', () => {
  beforeEach(() => {
    localStorageMock.clear();
    jest.clearAllMocks();
  });

  describe('security.sanitizeInput', () => {
    it('should sanitize dangerous characters', () => {
      const dangerous = '<script>alert("xss")</script>';
      const sanitized = security.sanitizeInput(dangerous);
      
      expect(sanitized).not.toContain('<script>');
      expect(sanitized).not.toContain('</script>');
      expect(sanitized).toContain('&lt;script&gt;');
    });

    it('should preserve safe content', () => {
      const safe = 'This is safe content with numbers 123';
      const sanitized = security.sanitizeInput(safe);
      
      expect(sanitized).toBe(safe);
    });

    it('should handle empty and non-string inputs', () => {
      expect(security.sanitizeInput('')).toBe('');
      expect(security.sanitizeInput(null)).toBe(null);
      expect(security.sanitizeInput(undefined)).toBe(undefined);
      expect(security.sanitizeInput(123)).toBe(123);
    });

    it('should trim whitespace', () => {
      const input = '  spaced content  ';
      const sanitized = security.sanitizeInput(input);
      
      expect(sanitized).toBe('spaced content');
    });
  });

  describe('security.validatePasswordStrength', () => {
    it('should accept strong passwords', () => {
      const strongPasswords = [
        'StrongP@ssw0rd!',
        'Complex1tyRul3s#',
        'Secure&P@ssw0rd2023'
      ];

      strongPasswords.forEach(password => {
        const result = security.validatePasswordStrength(password);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
        expect(result.score).toBeGreaterThan(70);
      });
    });

    it('should reject weak passwords', () => {
      const weakPasswords = [
        'weak',           // Too short
        'password',       // Common pattern
        '12345678',       // Only numbers
        'abcdefgh',       // Only lowercase
        'ABCDEFGH',       // Only uppercase
        'Password1',      // Missing special char
        'admin123'        // Forbidden pattern
      ];

      weakPasswords.forEach(password => {
        const result = security.validatePasswordStrength(password);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });

    it('should calculate password scores correctly', () => {
      const testCases = [
        { password: 'weak', expectedScore: 0 },
        { password: 'StrongP@ssw0rd!', expectedScore: 80 },
        { password: 'abc', expectedScore: 0 }
      ];

      testCases.forEach(({ password, expectedScore }) => {
        const result = security.validatePasswordStrength(password);
        expect(result.score).toBeGreaterThanOrEqual(expectedScore - 10);
      });
    });

    it('should detect forbidden patterns', () => {
      const forbiddenPasswords = [
        'Password123!',  // Contains "password"
        'Admin@123',     // Contains "admin"
        'Qwerty!123'     // Contains "qwerty"
      ];

      forbiddenPasswords.forEach(password => {
        const result = security.validatePasswordStrength(password);
        expect(result.isValid).toBe(false);
        expect(result.errors.some(error => 
          error.includes('patrones comunes')
        )).toBe(true);
      });
    });
  });

  describe('security.generateSecureToken', () => {
    it('should generate tokens of specified length', () => {
      const lengths = [16, 32, 64];
      
      lengths.forEach(length => {
        const token = security.generateSecureToken(length);
        expect(token).toHaveLength(length * 2); // Hex encoding doubles length
        expect(/^[a-f0-9]+$/.test(token)).toBe(true);
      });
    });

    it('should generate unique tokens', () => {
      const tokens = new Set();
      
      for (let i = 0; i < 100; i++) {
        const token = security.generateSecureToken(16);
        expect(tokens.has(token)).toBe(false);
        tokens.add(token);
      }
    });
  });

  describe('security.detectThreats', () => {
    it('should detect SQL injection', () => {
      const sqlInputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "SELECT * FROM passwords"
      ];

      sqlInputs.forEach(input => {
        const threats = security.detectThreats(input);
        expect(threats).toContain('SQL_INJECTION');
      });
    });

    it('should detect XSS attempts', () => {
      const xssInputs = [
        '<script>alert("xss")</script>',
        'javascript:alert(1)',
        '<img onerror="alert(1)" src="x">'
      ];

      xssInputs.forEach(input => {
        const threats = security.detectThreats(input);
        expect(threats).toContain('XSS');
      });
    });

    it('should detect path traversal', () => {
      const pathInputs = [
        '../../../etc/passwd',
        '..\\..\\windows\\system32'
      ];

      pathInputs.forEach(input => {
        const threats = security.detectThreats(input);
        expect(threats).toContain('PATH_TRAVERSAL');
      });
    });

    it('should detect command injection', () => {
      const cmdInputs = [
        'file.txt; rm -rf /',
        'data | cat /etc/passwd',
        'input && malicious_command'
      ];

      cmdInputs.forEach(input => {
        const threats = security.detectThreats(input);
        expect(threats).toContain('COMMAND_INJECTION');
      });
    });

    it('should return empty array for safe input', () => {
      const safeInputs = [
        'normal text',
        'user@example.com',
        'Safe filename.pdf',
        '12345'
      ];

      safeInputs.forEach(input => {
        const threats = security.detectThreats(input);
        expect(threats).toHaveLength(0);
      });
    });
  });

  describe('security.getSecureHeaders', () => {
    it('should return security headers', () => {
      const headers = security.getSecureHeaders();
      
      expect(headers).toHaveProperty('X-Content-Type-Options', 'nosniff');
      expect(headers).toHaveProperty('X-Frame-Options', 'DENY');
      expect(headers).toHaveProperty('X-XSS-Protection', '1; mode=block');
      expect(headers).toHaveProperty('Referrer-Policy');
      expect(headers).toHaveProperty('Cache-Control');
    });
  });

  describe('sessionManager', () => {
    describe('trackActivity', () => {
      it('should update last activity timestamp', () => {
        const beforeTime = Date.now();
        
        sessionManager.trackActivity();
        
        const afterTime = Date.now();
        const lastActivity = parseInt(localStorage.getItem('lastActivity'));
        
        expect(lastActivity).toBeGreaterThanOrEqual(beforeTime);
        expect(lastActivity).toBeLessThanOrEqual(afterTime);
      });
    });

    describe('isSessionExpired', () => {
      it('should return true when no activity recorded', () => {
        expect(sessionManager.isSessionExpired()).toBe(true);
      });

      it('should return false for recent activity', () => {
        sessionManager.trackActivity();
        expect(sessionManager.isSessionExpired()).toBe(false);
      });

      it('should return true for old activity', () => {
        const oldTime = Date.now() - (SECURITY_CONFIG.SESSION.MAX_IDLE_TIME + 1000);
        localStorage.setItem('lastActivity', oldTime.toString());
        
        expect(sessionManager.isSessionExpired()).toBe(true);
      });
    });

    describe('getTimeUntilExpiry', () => {
      it('should return 0 when no activity', () => {
        expect(sessionManager.getTimeUntilExpiry()).toBe(0);
      });

      it('should return positive time for recent activity', () => {
        sessionManager.trackActivity();
        const timeLeft = sessionManager.getTimeUntilExpiry();
        
        expect(timeLeft).toBeGreaterThan(0);
        expect(timeLeft).toBeLessThanOrEqual(SECURITY_CONFIG.SESSION.MAX_IDLE_TIME);
      });

      it('should return 0 for expired sessions', () => {
        const oldTime = Date.now() - (SECURITY_CONFIG.SESSION.MAX_IDLE_TIME + 1000);
        localStorage.setItem('lastActivity', oldTime.toString());
        
        expect(sessionManager.getTimeUntilExpiry()).toBe(0);
      });
    });

    describe('initSessionMonitoring', () => {
      it('should call onExpiry when session expires', (done) => {
        const onExpiry = jest.fn();
        const onWarning = jest.fn();
        
        // Set expired activity
        const oldTime = Date.now() - (SECURITY_CONFIG.SESSION.MAX_IDLE_TIME + 1000);
        localStorage.setItem('lastActivity', oldTime.toString());
        
        const cleanup = sessionManager.initSessionMonitoring(onExpiry, onWarning);
        
        // Wait for session check
        setTimeout(() => {
          expect(onExpiry).toHaveBeenCalled();
          cleanup();
          done();
        }, 100);
      });

      it('should call onWarning when session near expiry', (done) => {
        const onExpiry = jest.fn();
        const onWarning = jest.fn();
        
        // Set activity near expiry
        const nearExpiry = Date.now() - (SECURITY_CONFIG.SESSION.MAX_IDLE_TIME - 1000);
        localStorage.setItem('lastActivity', nearExpiry.toString());
        
        const cleanup = sessionManager.initSessionMonitoring(onExpiry, onWarning);
        
        // Wait for session check
        setTimeout(() => {
          expect(onWarning).toHaveBeenCalled();
          expect(onExpiry).not.toHaveBeenCalled();
          cleanup();
          done();
        }, 100);
      });
    });
  });

  describe('SECURITY_CONFIG', () => {
    it('should have required password settings', () => {
      expect(SECURITY_CONFIG.PASSWORD.MIN_LENGTH).toBeGreaterThan(0);
      expect(SECURITY_CONFIG.PASSWORD.REQUIRE_UPPERCASE).toBe(true);
      expect(SECURITY_CONFIG.PASSWORD.REQUIRE_LOWERCASE).toBe(true);
      expect(SECURITY_CONFIG.PASSWORD.REQUIRE_NUMBERS).toBe(true);
      expect(SECURITY_CONFIG.PASSWORD.REQUIRE_SPECIAL_CHARS).toBe(true);
      expect(Array.isArray(SECURITY_CONFIG.PASSWORD.FORBIDDEN_PATTERNS)).toBe(true);
    });

    it('should have session timeout settings', () => {
      expect(SECURITY_CONFIG.SESSION.TIMEOUT_WARNING).toBeGreaterThan(0);
      expect(SECURITY_CONFIG.SESSION.MAX_IDLE_TIME).toBeGreaterThan(0);
      expect(SECURITY_CONFIG.SESSION.REFRESH_INTERVAL).toBeGreaterThan(0);
    });

    it('should have rate limiting settings', () => {
      expect(SECURITY_CONFIG.RATE_LIMIT.LOGIN_ATTEMPTS).toBeGreaterThan(0);
      expect(SECURITY_CONFIG.RATE_LIMIT.WINDOW_MS).toBeGreaterThan(0);
      expect(SECURITY_CONFIG.RATE_LIMIT.BLOCK_DURATION).toBeGreaterThan(0);
    });
  });
});