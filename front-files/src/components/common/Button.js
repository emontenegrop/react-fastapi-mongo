// src/components/common/Button.js
import React from 'react';
import { Loader2 } from 'lucide-react';

const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  fullWidth = false,
  className = '',
  type = 'button',
  onClick,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    warning: 'bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500',
    info: 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-400',
    outline: 'border-2 border-gray-300 text-gray-700 hover:border-gray-400 hover:bg-gray-50 focus:ring-gray-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    link: 'text-blue-600 hover:text-blue-700 underline focus:ring-blue-500'
  };

  const sizeClasses = {
    small: 'px-3 py-2 text-sm',
    medium: 'px-4 py-2 text-sm',
    large: 'px-6 py-3 text-base',
    xlarge: 'px-8 py-4 text-lg'
  };

  const iconSizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-4 h-4',
    large: 'w-5 h-5',
    xlarge: 'w-6 h-6'
  };

  const isDisabled = disabled || loading;

  const buttonClasses = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    fullWidth ? 'w-full' : '',
    className
  ].filter(Boolean).join(' ');

  const iconClasses = iconSizeClasses[size];
  const hasIcon = Icon && !loading;
  const hasChildren = children !== undefined && children !== null;

  return (
    <button
      type={type}
      className={buttonClasses}
      disabled={isDisabled}
      onClick={onClick}
      {...props}
    >
      {/* Loading spinner */}
      {loading && (
        <Loader2 className={`${iconClasses} animate-spin ${hasChildren ? 'mr-2' : ''}`} />
      )}

      {/* Left icon */}
      {hasIcon && iconPosition === 'left' && (
        <Icon className={`${iconClasses} ${hasChildren ? 'mr-2' : ''}`} />
      )}

      {/* Children content */}
      {hasChildren && (
        <span>{children}</span>
      )}

      {/* Right icon */}
      {hasIcon && iconPosition === 'right' && (
        <Icon className={`${iconClasses} ${hasChildren ? 'ml-2' : ''}`} />
      )}
    </button>
  );
};

// Specific button variants for common use cases
export const PrimaryButton = (props) => <Button variant="primary" {...props} />;
export const SecondaryButton = (props) => <Button variant="secondary" {...props} />;
export const DangerButton = (props) => <Button variant="danger" {...props} />;
export const SuccessButton = (props) => <Button variant="success" {...props} />;
export const OutlineButton = (props) => <Button variant="outline" {...props} />;
export const GhostButton = (props) => <Button variant="ghost" {...props} />;
export const LinkButton = (props) => <Button variant="link" {...props} />;

export default Button;