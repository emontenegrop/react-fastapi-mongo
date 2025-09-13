// src/components/common/Input.js
import React, { useState, forwardRef } from 'react';
import { Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';

const Input = forwardRef(({
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  onBlur,
  onFocus,
  disabled = false,
  required = false,
  error,
  success,
  helperText,
  icon: Icon,
  iconPosition = 'left',
  className = '',
  inputClassName = '',
  size = 'medium',
  fullWidth = true,
  autoComplete,
  ...props
}, ref) => {
  const [showPassword, setShowPassword] = useState(false);
  const [focused, setFocused] = useState(false);

  const isPassword = type === 'password';
  const hasError = !!error;
  const hasSuccess = !!success;
  const hasIcon = !!Icon;
  const hasPasswordToggle = isPassword;

  const sizeClasses = {
    small: 'px-3 py-2 text-sm',
    medium: 'px-3 py-3 text-sm',
    large: 'px-4 py-4 text-base'
  };

  const iconSizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-5 h-5',
    large: 'w-6 h-6'
  };

  const baseInputClasses = [
    'block border rounded-lg transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-0',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50',
    sizeClasses[size],
    fullWidth ? 'w-full' : '',
    hasIcon && iconPosition === 'left' ? 'pl-10' : '',
    hasIcon && iconPosition === 'right' ? 'pr-10' : '',
    hasPasswordToggle ? 'pr-10' : '',
    hasError ? 'border-red-300 bg-red-50 focus:ring-red-500 focus:border-red-500' :
    hasSuccess ? 'border-green-300 bg-green-50 focus:ring-green-500 focus:border-green-500' :
    focused ? 'border-blue-300 bg-white focus:ring-blue-500 focus:border-blue-500' :
    'border-gray-300 bg-white hover:border-gray-400 focus:ring-blue-500 focus:border-blue-500',
    inputClassName
  ].filter(Boolean).join(' ');

  const containerClasses = [
    'relative',
    fullWidth ? 'w-full' : 'inline-block',
    className
  ].filter(Boolean).join(' ');

  const iconClasses = [
    'absolute top-1/2 transform -translate-y-1/2 pointer-events-none',
    iconSizeClasses[size],
    hasError ? 'text-red-400' :
    hasSuccess ? 'text-green-400' :
    focused ? 'text-blue-400' : 'text-gray-400',
    iconPosition === 'left' ? 'left-3' : 'right-3'
  ].filter(Boolean).join(' ');

  const handleFocus = (e) => {
    setFocused(true);
    onFocus?.(e);
  };

  const handleBlur = (e) => {
    setFocused(false);
    onBlur?.(e);
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

  return (
    <div className={containerClasses}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Input container */}
      <div className="relative">
        {/* Left icon */}
        {hasIcon && iconPosition === 'left' && (
          <Icon className={iconClasses} />
        )}

        {/* Input field */}
        <input
          ref={ref}
          type={inputType}
          value={value}
          onChange={onChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          disabled={disabled}
          required={required}
          placeholder={placeholder}
          autoComplete={autoComplete}
          className={baseInputClasses}
          {...props}
        />

        {/* Right icon */}
        {hasIcon && iconPosition === 'right' && !hasPasswordToggle && (
          <Icon className={iconClasses} />
        )}

        {/* Password toggle */}
        {hasPasswordToggle && (
          <button
            type="button"
            onClick={togglePasswordVisibility}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
            tabIndex={-1}
          >
            {showPassword ? (
              <EyeOff className={iconSizeClasses[size]} />
            ) : (
              <Eye className={iconSizeClasses[size]} />
            )}
          </button>
        )}

        {/* Status icons */}
        {hasError && !hasIcon && !hasPasswordToggle && (
          <AlertCircle className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-red-400" />
        )}
        
        {hasSuccess && !hasIcon && !hasPasswordToggle && (
          <CheckCircle className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-green-400" />
        )}
      </div>

      {/* Helper text, error, or success message */}
      {(helperText || error || success) && (
        <div className="mt-2">
          {error && (
            <p className="text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
              {error}
            </p>
          )}
          
          {success && !error && (
            <p className="text-sm text-green-600 flex items-center">
              <CheckCircle className="w-4 h-4 mr-1 flex-shrink-0" />
              {success}
            </p>
          )}
          
          {helperText && !error && !success && (
            <p className="text-sm text-gray-500">
              {helperText}
            </p>
          )}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;