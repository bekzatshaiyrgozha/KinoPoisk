import { cn } from '@/utils';
import type { ButtonProps } from './Button.types';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  isLoading = false,
  disabled,
  className,
  ...props
}: ButtonProps) => {
  return (
    <button
      disabled={disabled || isLoading}
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-medium transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        // Size variants
        size === 'sm' && 'px-3 py-1.5 text-sm',
        size === 'md' && 'px-4 py-2 text-base',
        size === 'lg' && 'px-6 py-3 text-lg',
        // Color variants
        variant === 'primary' &&
          'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
        variant === 'secondary' &&
          'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
        variant === 'danger' &&
          'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
        variant === 'ghost' &&
          'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
        // Full width
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {isLoading ? (
        <span className="inline-block animate-spin mr-2">⌛</span>
      ) : null}
      {children}
    </button>
  );
};
