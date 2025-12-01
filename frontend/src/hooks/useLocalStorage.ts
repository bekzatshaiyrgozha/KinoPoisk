import { useState } from 'react';
import { storage } from '@/utils/storage';

export function useLocalStorage<T>(key: string, initialValue: T, maxAge?: number) {
  const [value, setValue] = useState<T>(() => storage.get<T>(key) ?? initialValue);

  const setStoredValue = (newValue: T | ((val: T) => T)) => {
    const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
    setValue(valueToStore);
    storage.set(key, valueToStore, maxAge);
  };

  return [value, setStoredValue] as const;
}
