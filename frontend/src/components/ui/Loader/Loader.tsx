import { cn } from '@/utils';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Loader = ({ size = 'md', className }: LoaderProps) => {
  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div
        className={cn(
          'animate-spin rounded-full border-4 border-gray-200 border-t-primary-600',
          size === 'sm' && 'h-6 w-6',
          size === 'md' && 'h-10 w-10',
          size === 'lg' && 'h-16 w-16'
        )}
      />
    </div>
  );
};
