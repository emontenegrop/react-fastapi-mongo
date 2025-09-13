// src/__tests__/setup.js
import '@testing-library/jest-dom';

// Mock crypto.getRandomValues for security.generateSecureToken
Object.defineProperty(global, 'crypto', {
  value: {
    getRandomValues: (arr) => {
      for (let i = 0; i < arr.length; i++) {
        arr[i] = Math.floor(Math.random() * 256);
      }
      return arr;
    },
    subtle: {
      digest: jest.fn(() => Promise.resolve(new ArrayBuffer(32)))
    }
  }
});

// Mock window.location
delete window.location;
window.location = {
  href: 'http://localhost:3000',
  protocol: 'http:',
  hostname: 'localhost',
  pathname: '/'
};

// Mock matchMedia for responsive components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Suppress console warnings during tests
const originalConsoleWarn = console.warn;
console.warn = (message, ...args) => {
  // Suppress specific warnings that are expected during testing
  if (
    typeof message === 'string' &&
    (
      message.includes('Warning: ReactDOM.render is deprecated') ||
      message.includes('Warning: validateDOMNesting') ||
      message.includes('Act warning')
    )
  ) {
    return;
  }
  originalConsoleWarn(message, ...args);
};

// Mock environment variables
process.env.REACT_APP_API_URL = 'http://localhost:8082';
process.env.NODE_ENV = 'test';

// Global test utilities
global.testUtils = {
  // Helper to create mock API responses
  createMockResponse: (data, status = 200) => ({
    data,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: {},
    config: {}
  }),

  // Helper to create mock errors
  createMockError: (message, status = 500) => {
    const error = new Error(message);
    error.response = {
      status,
      data: { message },
      statusText: status === 500 ? 'Internal Server Error' : 'Error'
    };
    return error;
  },

  // Helper to wait for async operations
  waitForNextTick: () => new Promise(resolve => setTimeout(resolve, 0)),

  // Helper to create form data
  createFormData: (fields) => {
    const formData = new FormData();
    Object.entries(fields).forEach(([key, value]) => {
      formData.append(key, value);
    });
    return formData;
  }
};

// Setup for localStorage mock
const localStorageMock = {
  store: {},
  getItem: function(key) {
    return this.store[key] || null;
  },
  setItem: function(key, value) {
    this.store[key] = value.toString();
  },
  removeItem: function(key) {
    delete this.store[key];
  },
  clear: function() {
    this.store = {};
  }
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Setup for sessionStorage mock
const sessionStorageMock = {
  store: {},
  getItem: function(key) {
    return this.store[key] || null;
  },
  setItem: function(key, value) {
    this.store[key] = value.toString();
  },
  removeItem: function(key) {
    delete this.store[key];
  },
  clear: function() {
    this.store = {};
  }
};

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock
});

// Clean up after each test
afterEach(() => {
  // Clear localStorage and sessionStorage
  localStorageMock.clear();
  sessionStorageMock.clear();
  
  // Clear all mocks
  jest.clearAllMocks();
  
  // Reset any timers
  jest.useRealTimers();
});

// Global error handler for unhandled promise rejections in tests
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Increase test timeout for integration tests
jest.setTimeout(10000);