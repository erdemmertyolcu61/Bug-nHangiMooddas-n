import { useState, useEffect, useRef, useCallback } from 'react';
import { getDuelloState } from '../services/api';

export default function useDuelloPoll(roomId, enabled = true, intervalMs = 2500) {
  const [state, setState] = useState(null);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);
  const mountedRef = useRef(true);

  const poll = useCallback(async () => {
    if (!roomId || !mountedRef.current) return;
    try {
      const data = await getDuelloState(roomId);
      if (mountedRef.current) {
        setState(data);
        setError(null);
      }
    } catch (e) {
      if (mountedRef.current) setError(e);
    }
  }, [roomId]);

  useEffect(() => {
    mountedRef.current = true;
    if (!roomId || !enabled) {
      setState(null);
      return;
    }

    poll();
    intervalRef.current = setInterval(poll, intervalMs);

    const onVisibility = () => {
      if (document.visibilityState === 'visible') {
        poll();
        if (!intervalRef.current) {
          intervalRef.current = setInterval(poll, intervalMs);
        }
      } else {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      mountedRef.current = false;
      clearInterval(intervalRef.current);
      intervalRef.current = null;
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [roomId, enabled, intervalMs, poll]);

  return { state, error, refetch: poll };
}
