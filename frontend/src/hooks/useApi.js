import { useState, useCallback } from 'react';
import { api } from '../api/client';

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const request = useCallback(async (method, endpoint, body) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api[method](endpoint, body);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, request };
}
