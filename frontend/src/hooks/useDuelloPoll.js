import { useState, useEffect, useRef, useCallback } from 'react';
import { getDuelloState } from '../services/api';

export default function useDuelloPoll(roomId, enabled = true, intervalMs = 1500) {
  const [state, setState] = useState(null);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);
  const mountedRef = useRef(true);
  const failCount = useRef(0);

  const poll = useCallback(async () => {
    if (!roomId || !mountedRef.current) return;
    try {
      const data = await getDuelloState(roomId);
      if (mountedRef.current) {
        setState(data);
        setError(null);
        failCount.current = 0;
      }
    } catch (e) {
      if (mountedRef.current) {
        failCount.current++;
        setError(e);
        // after 20 consecutive failures (~30s), clear state so UI can react
        if (failCount.current > 20) setState(null);
      }
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
        clearInterval(intervalRef.current);
        intervalRef.current = setInterval(poll, intervalMs);
      } else {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };

    const onOnline = () => { poll(); };

    document.addEventListener('visibilitychange', onVisibility);
    window.addEventListener('online', onOnline);

    return () => {
      mountedRef.current = false;
      clearInterval(intervalRef.current);
      intervalRef.current = null;
      document.removeEventListener('visibilitychange', onVisibility);
      window.removeEventListener('online', onOnline);
    };
  }, [roomId, enabled, intervalMs, poll]);

  return { state, error, refetch: poll };
}
