import { cn } from '@/utils';
import type { CardProps } from './Card.types';

export const Card = ({
  children,
  padding = 'md',
  shadow = 'md',
  hover = false,
  className,
  ...props
}: CardProps) => {
  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-gray-200',
        // Padding
        padding === 'sm' && 'p-3',
        padding === 'md' && 'p-4',
        padding === 'lg' && 'p-6',
        padding === 'none' && 'p-0',
        // Shadow
        shadow === 'sm' && 'shadow-sm',
        shadow === 'md' && 'shadow-md',
        shadow === 'lg' && 'shadow-lg',
        shadow === 'none' && 'shadow-none',
        // Hover effect
        hover && 'transition-shadow hover:shadow-lg',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
