import { useRef, useCallback } from 'react';

/**
 * Хук для throttling функции - ограничивает частоту вызовов
 * @param callback - функция для throttling
 * @param delay - задержка в миллисекундах
 * @returns throttled версию функции
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 1000
): T {
  const lastRun = useRef<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  return useCallback(
    ((...args: Parameters<T>) => {
      const now = Date.now();
      const timeSinceLastRun = now - lastRun.current;

      if (timeSinceLastRun >= delay) {
        // Можно выполнить сразу
        lastRun.current = now;
        callback(...args);
      } else {
        // Нужно подождать
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        timeoutRef.current = setTimeout(() => {
          lastRun.current = Date.now();
          callback(...args);
          timeoutRef.current = null;
        }, delay - timeSinceLastRun);
      }
    }) as T,
    [callback, delay]
  );
}

