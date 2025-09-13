// src/components/common/LoadingSpinner.js
import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ size = 'default', text = 'Cargando...', className = '' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    default: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className={`flex items-center justify-center min-h-screen bg-gray-50 ${className}`}>
      <div className="text-center">
        <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-600 mx-auto mb-4`} />
        <p className="text-gray-600 text-sm">{text}</p>
      </div>
    </div>
  );
};

// Inline loading spinner for smaller components
export const InlineSpinner = ({ size = 'small', className = '' }) => (
  <Loader2 className={`${size === 'small' ? 'w-4 h-4' : 'w-6 h-6'} animate-spin ${className}`} />
);

// Button loading spinner
export const ButtonSpinner = ({ className = '' }) => (
  <Loader2 className={`w-4 h-4 animate-spin ${className}`} />
);

export default LoadingSpinner;