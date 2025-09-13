// src/__tests__/components/LoginPage.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../../pages/LoginPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { ToastProvider } from '../../components/common/Toast';

// Mock the hooks and modules
jest.mock('../../utils/validation', () => ({
  validationSchemas: {
    login: {
      validate: jest.fn()
    }
  },
  rateLimiter: {
    isBlocked: jest.fn(() => false),
    recordAttempt: jest.fn(),
    getRemainingTime: jest.fn(() => 0)
  }
}));

// Mock auth context
const mockLogin = jest.fn();
const mockClearError = jest.fn();

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
    error: null,
    clearError: mockClearError,
    loading: false
  }),
  AuthProvider: ({ children }) => <div>{children}</div>
}));

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <ToastProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </ToastProvider>
  </BrowserRouter>
);

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render login form', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    expect(screen.getByText('Iniciar Sesión')).toBeInTheDocument();
    expect(screen.getByLabelText(/correo electrónico/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('should show/hide password when toggle button is clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const passwordInput = screen.getByLabelText(/contraseña/i);
    const toggleButton = screen.getByRole('button', { name: /mostrar contraseña/i });

    // Initially password should be hidden
    expect(passwordInput.type).toBe('password');

    // Click toggle to show password
    await user.click(toggleButton);
    expect(passwordInput.type).toBe('text');

    // Click toggle to hide password again
    await user.click(toggleButton);
    expect(passwordInput.type).toBe('password');
  });

  it('should submit form with valid data', async () => {
    const user = userEvent.setup();
    mockLogin.mockResolvedValue({ success: true });

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/correo electrónico/i);
    const passwordInput = screen.getByLabelText(/contraseña/i);
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });

    // Fill form
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');

    // Submit form
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('should display validation errors', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });

    // Submit empty form
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email es requerido/i)).toBeInTheDocument();
    });
  });

  it('should display login error', async () => {
    const user = userEvent.setup();
    const errorMessage = 'Credenciales inválidas';
    mockLogin.mockRejectedValue(new Error(errorMessage));

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/correo electrónico/i);
    const passwordInput = screen.getByLabelText(/contraseña/i);
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });

    // Fill and submit form
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('should disable form when loading', () => {
    // Mock loading state
    jest.doMock('../../contexts/AuthContext', () => ({
      useAuth: () => ({
        login: mockLogin,
        error: null,
        clearError: mockClearError,
        loading: true
      })
    }));

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/correo electrónico/i);
    const passwordInput = screen.getByLabelText(/contraseña/i);
    const submitButton = screen.getByRole('button', { name: /iniciando sesión/i });

    expect(emailInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });

  it('should display rate limiting warning', () => {
    // Mock rate limiting
    jest.doMock('../../utils/validation', () => ({
      rateLimiter: {
        isBlocked: jest.fn(() => true),
        getRemainingTime: jest.fn(() => 300000) // 5 minutes
      }
    }));

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    expect(screen.getByText(/cuenta temporalmente bloqueada/i)).toBeInTheDocument();
    expect(screen.getByText(/tiempo restante/i)).toBeInTheDocument();
  });

  it('should have forgot password link', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const forgotPasswordLink = screen.getByRole('link', { name: /olvidaste tu contraseña/i });
    expect(forgotPasswordLink).toBeInTheDocument();
    expect(forgotPasswordLink.getAttribute('href')).toBe('/forgot-password');
  });

  it('should handle keyboard navigation', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/correo electrónico/i);
    const passwordInput = screen.getByLabelText(/contraseña/i);

    // Tab navigation
    await user.tab();
    expect(emailInput).toHaveFocus();

    await user.tab();
    expect(passwordInput).toHaveFocus();

    // Enter key should submit form
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled();
    });
  });

  it('should sanitize input values', async () => {
    const user = userEvent.setup();
    mockLogin.mockResolvedValue({ success: true });

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/correo electrónico/i);
    const passwordInput = screen.getByLabelText(/contraseña/i);
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });

    // Type malicious input
    await user.type(emailInput, 'test@example.com<script>alert("xss")</script>');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    await waitFor(() => {
      // Should call login with sanitized email
      expect(mockLogin).toHaveBeenCalledWith(
        expect.not.stringContaining('<script>'),
        'password123'
      );
    });
  });

  it('should clear errors when user starts typing', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/correo electrónico/i);

    // Start typing should clear errors
    await user.type(emailInput, 'test');

    expect(mockClearError).toHaveBeenCalled();
  });
});