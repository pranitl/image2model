import React from 'react';

interface BadgeProps {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning';
  className?: string;
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'default', className = '', children }) => {
  const baseClasses = 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2';
  
  const variantClasses = {
    default: 'border-transparent bg-gray-900 text-gray-50 hover:bg-gray-900/80',
    secondary: 'border-transparent bg-gray-100 text-gray-900 hover:bg-gray-100/80',
    destructive: 'border-transparent bg-red-500 text-gray-50 hover:bg-red-500/80',
    outline: 'text-gray-950 border-gray-300',
    success: 'border-transparent bg-green-500 text-white hover:bg-green-500/80',
    warning: 'border-transparent bg-yellow-500 text-white hover:bg-yellow-500/80'
  };
  
  return (
    <div className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {children}
    </div>
  );
};