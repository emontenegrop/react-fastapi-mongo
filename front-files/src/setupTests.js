// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
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

// Mock environment variables
process.env.REACT_APP_API_URL = 'http://localhost:8082';
process.env.NODE_ENV = 'test';

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

// Clean up after each test
afterEach(() => {
  localStorageMock.clear();
  jest.clearAllMocks();
});
