// src/__tests__/utils/validation.test.js
import { validationSchemas, security, rateLimiter, validateForm } from '../../utils/validation';

describe('Validation Utils', () => {
  describe('validationSchemas', () => {
    describe('login schema', () => {
      it('should validate correct login data', async () => {
        const validData = {
          email: 'test@example.com',
          password: 'validPassword123'
        };

        const result = await validateForm(validationSchemas.login, validData);
        expect(result.success).toBe(true);
        expect(result.data.email).toBe('test@example.com');
      });

      it('should reject invalid email', async () => {
        const invalidData = {
          email: 'invalid-email',
          password: 'validPassword123'
        };

        const result = await validateForm(validationSchemas.login, invalidData);
        expect(result.success).toBe(false);
        expect(result.errors.email).toBeDefined();
      });

      it('should require password', async () => {
        const invalidData = {
          email: 'test@example.com',
          password: ''
        };

        const result = await validateForm(validationSchemas.login, invalidData);
        expect(result.success).toBe(false);
        expect(result.errors.password).toBeDefined();
      });

      it('should normalize email to lowercase', async () => {
        const data = {
          email: 'TEST@EXAMPLE.COM',
          password: 'validPassword123'
        };

        const result = await validateForm(validationSchemas.login, data);
        expect(result.success).toBe(true);
        expect(result.data.email).toBe('test@example.com');
      });
    });

    describe('password schema', () => {
      it('should validate strong password', async () => {
        const validData = {
          password: 'StrongP@ssw0rd!',
          confirmPassword: 'StrongP@ssw0rd!'
        };

        const result = await validateForm(validationSchemas.password, validData);
        expect(result.success).toBe(true);
      });

      it('should reject weak password', async () => {
        const invalidData = {
          password: 'weak',
          confirmPassword: 'weak'
        };

        const result = await validateForm(validationSchemas.password, invalidData);
        expect(result.success).toBe(false);
        expect(result.errors.password).toBeDefined();
      });

      it('should require password confirmation match', async () => {
        const invalidData = {
          password: 'StrongP@ssw0rd!',
          confirmPassword: 'DifferentP@ssw0rd!'
        };

        const result = await validateForm(validationSchemas.password, invalidData);
        expect(result.success).toBe(false);
        expect(result.errors.confirmPassword).toBeDefined();
      });
    });
  });

  describe('security functions', () => {
    describe('hasSQLInjection', () => {
      it('should detect SQL injection attempts', () => {
        const sqlInjections = [
          "'; DROP TABLE users; --",
          "1' OR '1'='1",
          "admin'/*",
          "SELECT * FROM users"
        ];

        sqlInjections.forEach(injection => {
          expect(security.hasSQLInjection(injection)).toBe(true);
        });
      });

      it('should allow safe input', () => {
        const safeInputs = [
          'normal text',
          'user@example.com',
          'My name is John',
          '123456'
        ];

        safeInputs.forEach(input => {
          expect(security.hasSQLInjection(input)).toBe(false);
        });
      });
    });

    describe('hasXSS', () => {
      it('should detect XSS attempts', () => {
        const xssAttempts = [
          '<script>alert("xss")</script>',
          'javascript:alert("xss")',
          '<img onerror="alert(1)" src="x">',
          '<iframe src="javascript:alert(1)">',
          '<object data="javascript:alert(1)">'
        ];

        xssAttempts.forEach(xss => {
          expect(security.hasXSS(xss)).toBe(true);
        });
      });

      it('should allow safe HTML-like text', () => {
        const safeInputs = [
          'This is normal text',
          'Price < 100',
          'Math: 2 > 1',
          'Email: user@example.com'
        ];

        safeInputs.forEach(input => {
          expect(security.hasXSS(input)).toBe(false);
        });
      });
    });

    describe('hasPathTraversal', () => {
      it('should detect path traversal attempts', () => {
        const pathTraversals = [
          '../../../etc/passwd',
          '..\\..\\windows\\system32',
          './../../config',
          '../.env'
        ];

        pathTraversals.forEach(path => {
          expect(security.hasPathTraversal(path)).toBe(true);
        });
      });

      it('should allow normal paths', () => {
        const normalPaths = [
          'documents/file.pdf',
          'images/photo.jpg',
          'reports/2023/january.xlsx',
          'profile-picture.png'
        ];

        normalPaths.forEach(path => {
          expect(security.hasPathTraversal(path)).toBe(false);
        });
      });
    });

    describe('isSecure', () => {
      it('should reject any malicious input', () => {
        const maliciousInputs = [
          '<script>alert("xss")</script>',
          "'; DROP TABLE users; --",
          '../../../etc/passwd',
          'javascript:alert(1)'
        ];

        maliciousInputs.forEach(input => {
          expect(security.isSecure(input)).toBe(false);
        });
      });

      it('should accept safe input', () => {
        const safeInputs = [
          'normal text',
          'user@example.com',
          'Valid filename.pdf',
          'Some description with numbers 123'
        ];

        safeInputs.forEach(input => {
          expect(security.isSecure(input)).toBe(true);
        });
      });
    });
  });

  describe('rateLimiter', () => {
    beforeEach(() => {
      // Clear rate limiter state before each test
      rateLimiter.attempts.clear();
    });

    it('should allow requests within limit', () => {
      const key = 'test-key';
      
      // Record 3 attempts (below limit of 5)
      for (let i = 0; i < 3; i++) {
        rateLimiter.recordAttempt(key);
      }
      
      expect(rateLimiter.isBlocked(key)).toBe(false);
    });

    it('should block requests exceeding limit', () => {
      const key = 'test-key';
      
      // Record 6 attempts (exceeds limit of 5)
      for (let i = 0; i < 6; i++) {
        rateLimiter.recordAttempt(key);
      }
      
      expect(rateLimiter.isBlocked(key)).toBe(true);
    });

    it('should reset after time window', () => {
      const key = 'test-key';
      const windowMs = 100; // Short window for testing
      
      // Record attempts that exceed the limit
      for (let i = 0; i < 6; i++) {
        rateLimiter.recordAttempt(key);
      }
      
      expect(rateLimiter.isBlocked(key, 5, windowMs)).toBe(true);
      
      // Wait for window to expire
      setTimeout(() => {
        expect(rateLimiter.isBlocked(key, 5, windowMs)).toBe(false);
      }, windowMs + 10);
    });

    it('should calculate remaining time correctly', () => {
      const key = 'test-key';
      const windowMs = 1000;
      
      rateLimiter.recordAttempt(key);
      
      const remainingTime = rateLimiter.getRemainingTime(key, windowMs);
      expect(remainingTime).toBeGreaterThan(900);
      expect(remainingTime).toBeLessThanOrEqual(1000);
    });
  });

  describe('validateForm', () => {
    it('should perform security checks on all string values', async () => {
      const maliciousData = {
        name: '<script>alert("xss")</script>',
        email: 'test@example.com'
      };

      const schema = validationSchemas.profile;
      const result = await validateForm(schema, maliciousData);
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Contenido no válido detectado');
    });

    it('should sanitize and validate clean data', async () => {
      const cleanData = {
        firstName: 'John',
        lastName: 'Doe',
        email: 'john.doe@example.com',
        phone: '+1234567890'
      };

      const result = await validateForm(validationSchemas.profile, cleanData);
      expect(result.success).toBe(true);
      expect(result.data.firstName).toBe('John');
    });

    it('should handle validation errors correctly', async () => {
      const invalidData = {
        firstName: '', // Required field
        lastName: 'Doe',
        email: 'invalid-email', // Invalid email
        phone: 'abc123' // Invalid phone
      };

      const result = await validateForm(validationSchemas.profile, invalidData);
      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
      expect(Object.keys(result.errors).length).toBeGreaterThan(0);
    });
  });
});