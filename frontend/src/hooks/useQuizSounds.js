import { useRef, useCallback } from 'react';

/**
 * Web Audio API ile quiz ses efektleri.
 * Harici dosya gerektirmez — tüm sesler programatik üretilir.
 * İlk kullanıcı etkileşiminde AudioContext otomatik başlatılır.
 */
export default function useQuizSounds() {
  const ctxRef = useRef(null);

  const getCtx = useCallback(() => {
    if (!ctxRef.current) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctxRef.current = new AC();
    }
    if (ctxRef.current.state === 'suspended') {
      ctxRef.current.resume();
    }
    return ctxRef.current;
  }, []);

  const playCorrect = useCallback(() => {
    const ctx = getCtx();
    if (!ctx) return;
    const now = ctx.currentTime;

    // Rising two-tone chime
    [520, 780].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.18, now + i * 0.1);
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.1 + 0.3);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now + i * 0.1);
      osc.stop(now + i * 0.1 + 0.3);
    });
  }, [getCtx]);

  const playWrong = useCallback(() => {
    const ctx = getCtx();
    if (!ctx) return;
    const now = ctx.currentTime;

    // Low buzz
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(180, now);
    osc.frequency.linearRampToValueAtTime(120, now + 0.25);
    gain.gain.setValueAtTime(0.12, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
    osc.connect(gain).connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.3);
  }, [getCtx]);

  const playTick = useCallback(() => {
    const ctx = getCtx();
    if (!ctx) return;
    const now = ctx.currentTime;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = 880;
    gain.gain.setValueAtTime(0.1, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
    osc.connect(gain).connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.08);
  }, [getCtx]);

  const playJoker = useCallback(() => {
    const ctx = getCtx();
    if (!ctx) return;
    const now = ctx.currentTime;

    // Ascending sweep
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(400, now);
    osc.frequency.exponentialRampToValueAtTime(1200, now + 0.2);
    gain.gain.setValueAtTime(0.15, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
    osc.connect(gain).connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.35);
  }, [getCtx]);

  const warmUp = useCallback(() => {
    getCtx();
  }, [getCtx]);

  return { playCorrect, playWrong, playTick, playJoker, warmUp };
}
