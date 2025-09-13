// src/components/common/Card.js
import React from 'react';

const Card = ({
  children,
  title,
  subtitle,
  className = '',
  bodyClassName = '',
  headerClassName = '',
  variant = 'default',
  shadow = 'default',
  hover = false,
  clickable = false,
  onClick,
  padding = 'default'
}) => {
  const variantClasses = {
    default: 'bg-white border border-gray-200',
    primary: 'bg-blue-50 border border-blue-200',
    success: 'bg-green-50 border border-green-200',
    warning: 'bg-yellow-50 border border-yellow-200',
    danger: 'bg-red-50 border border-red-200',
    dark: 'bg-gray-800 border border-gray-700 text-white'
  };

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    default: 'shadow',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl'
  };

  const paddingClasses = {
    none: '',
    sm: 'p-3',
    default: 'p-6',
    lg: 'p-8'
  };

  const baseClasses = [
    'rounded-lg transition-all duration-200',
    variantClasses[variant],
    shadowClasses[shadow],
    hover ? 'hover:shadow-md' : '',
    clickable ? 'cursor-pointer hover:shadow-lg' : '',
    paddingClasses[padding],
    className
  ].filter(Boolean).join(' ');

  const CardComponent = clickable ? 'button' : 'div';

  return (
    <CardComponent
      className={baseClasses}
      onClick={clickable ? onClick : undefined}
    >
      {(title || subtitle) && (
        <div className={`mb-4 ${headerClassName}`}>
          {title && (
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-600">
              {subtitle}
            </p>
          )}
        </div>
      )}
      
      <div className={bodyClassName}>
        {children}
      </div>
    </CardComponent>
  );
};

// Specialized card components
export const StatsCard = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  className = '',
  ...props
}) => {
  const changeClasses = {
    positive: 'text-green-600',
    negative: 'text-red-600',
    neutral: 'text-gray-600'
  };

  return (
    <Card className={`${className}`} {...props}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 truncate">
            {title}
          </p>
          <p className="text-2xl font-semibold text-gray-900">
            {value}
          </p>
          {change && (
            <p className={`text-sm ${changeClasses[changeType]}`}>
              {change}
            </p>
          )}
        </div>
        
        {Icon && (
          <div className="ml-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Icon className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export const FeatureCard = ({
  icon: Icon,
  title,
  description,
  action,
  className = '',
  ...props
}) => {
  return (
    <Card className={`text-center ${className}`} {...props}>
      {Icon && (
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon className="w-8 h-8 text-blue-600" />
        </div>
      )}
      
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {title}
        </h3>
      )}
      
      {description && (
        <p className="text-gray-600 mb-4">
          {description}
        </p>
      )}
      
      {action}
    </Card>
  );
};

export const UserCard = ({
  avatar,
  name,
  email,
  role,
  status = 'active',
  actions,
  className = '',
  ...props
}) => {
  const statusClasses = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    pending: 'bg-yellow-100 text-yellow-800',
    suspended: 'bg-red-100 text-red-800'
  };

  return (
    <Card className={className} {...props}>
      <div className="flex items-center space-x-4">
        <div className="flex-shrink-0">
          {avatar ? (
            <img
              src={avatar}
              alt={name}
              className="w-12 h-12 rounded-full object-cover"
            />
          ) : (
            <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-gray-600 font-medium text-lg">
                {name?.charAt(0)?.toUpperCase()}
              </span>
            </div>
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <p className="text-sm font-medium text-gray-900 truncate">
              {name}
            </p>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClasses[status]}`}>
              {status}
            </span>
          </div>
          
          {email && (
            <p className="text-sm text-gray-500 truncate">
              {email}
            </p>
          )}
          
          {role && (
            <p className="text-xs text-gray-400 capitalize">
              {role}
            </p>
          )}
        </div>
        
        {actions && (
          <div className="flex-shrink-0">
            {actions}
          </div>
        )}
      </div>
    </Card>
  );
};

export const FileCard = ({
  fileName,
  fileSize,
  fileType,
  thumbnail,
  uploadDate,
  actions,
  className = '',
  ...props
}) => {
  const formatFileSize = (bytes) => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString();
  };

  return (
    <Card className={className} hover {...props}>
      <div className="space-y-3">
        {/* Thumbnail or file type icon */}
        <div className="aspect-square w-full bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
          {thumbnail ? (
            <img
              src={thumbnail}
              alt={fileName}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="text-gray-400 text-4xl">
              📄
            </div>
          )}
        </div>
        
        {/* File info */}
        <div>
          <p className="text-sm font-medium text-gray-900 truncate" title={fileName}>
            {fileName}
          </p>
          <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
            <span>{formatFileSize(fileSize)}</span>
            <span>{fileType}</span>
          </div>
          {uploadDate && (
            <p className="text-xs text-gray-400 mt-1">
              {formatDate(uploadDate)}
            </p>
          )}
        </div>
        
        {/* Actions */}
        {actions && (
          <div className="flex items-center justify-between">
            {actions}
          </div>
        )}
      </div>
    </Card>
  );
};

export default Card;