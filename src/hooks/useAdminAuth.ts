import { useState, useCallback } from 'react';
import { validatePin } from '../services/adminApi';

const SESSION_KEY = 'ig_admin_auth';

export function useAdminAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return sessionStorage.getItem(SESSION_KEY) === 'true';
  });
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const authenticate = useCallback(async (pin: string): Promise<boolean> => {
    setIsValidating(true);
    setError(null);
    try {
      const valid = await validatePin(pin);
      if (valid) {
        sessionStorage.setItem(SESSION_KEY, 'true');
        setIsAuthenticated(true);
        return true;
      } else {
        setError('Invalid PIN');
        return false;
      }
    } catch {
      setError('Authentication failed');
      return false;
    } finally {
      setIsValidating(false);
    }
  }, []);

  const logout = useCallback(() => {
    sessionStorage.removeItem(SESSION_KEY);
    setIsAuthenticated(false);
  }, []);

  return {
    isAuthenticated,
    isValidating,
    error,
    authenticate,
    logout,
    clearError: () => setError(null),
  };
}
