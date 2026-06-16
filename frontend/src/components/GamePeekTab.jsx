import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';

const DAILY_KEY = 'fc_oracle_last_played';
const todayStr = () => new Date().toISOString().slice(0, 10);
const hasPlayedToday = () => {
  try { return localStorage.getItem(DAILY_KEY) === todayStr(); } catch { return false; }
};

export default function GamePeekTab() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [ready, setReady] = useState(!hasPlayedToday());
  const [pulse, setPulse] = useState(true);

  useEffect(() => {
    const check = () => setReady(!hasPlayedToday());
    check();
    const id = setInterval(check, 30000);
    window.addEventListener('storage', check);
    window.addEventListener('oracle-updated', check);
    window.addEventListener('focus', check);
    return () => {
      clearInterval(id);
      window.removeEventListener('storage', check);
      window.removeEventListener('oracle-updated', check);
      window.removeEventListener('focus', check);
    };
  }, [pathname]);

  useEffect(() => {
    const t = setTimeout(() => setPulse(false), 8000);
    return () => clearTimeout(t);
  }, []);

  if (pathname !== '/discover' || !ready) return null;

  return (
    <motion.button
      onClick={() => navigate('/oyun')}
      aria-label="Mini oyun: Mood Kâhini"
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0, opacity: 0 }}
      transition={{ type: 'spring', stiffness: 400, damping: 20, delay: 1.2 }}
      whileTap={{ scale: 0.85 }}
      whileHover={{ scale: 1.08 }}
      className="
        fixed right-4 bottom-[11.5rem] mb-safe z-[95]
        flex flex-col items-center justify-center
        w-[58px] h-[58px] rounded-[18px]
        bg-gradient-to-br from-violet-500 via-fuchsia-500 to-amber-400
        shadow-[0_6px_28px_-4px_rgba(168,85,247,0.55),0_2px_8px_rgba(0,0,0,0.3)]
        border border-white/20
        cursor-pointer select-none
        overflow-visible
      "
    >
      {/* Outer glow ring */}
      <span className="pointer-events-none absolute -inset-1 rounded-[22px] border-2 border-violet-400/40 animate-[ping_3s_ease-in-out_infinite]" />

      {/* Shimmer overlay */}
      <span
        className="pointer-events-none absolute inset-0 rounded-[18px] overflow-hidden"
        style={{ mixBlendMode: 'overlay' }}
      >
        <span className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/30 to-transparent translate-x-[-100%] animate-[shimmer_3s_ease-in-out_infinite]" />
      </span>

      {/* Crystal ball emoji */}
      <span className="text-[26px] leading-none drop-shadow-[0_2px_4px_rgba(0,0,0,0.4)] relative z-10">
        🔮
      </span>

      {/* "Oyna" label */}
      <AnimatePresence>
        {pulse && (
          <motion.span
            initial={{ opacity: 0, y: 4, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ delay: 2, duration: 0.4 }}
            className="
              absolute -top-7 left-1/2 -translate-x-1/2
              px-2.5 py-0.5 rounded-full
              bg-white text-[10px] font-extrabold text-violet-600
              shadow-[0_2px_10px_rgba(0,0,0,0.15)]
              whitespace-nowrap
            "
          >
            Oyna!
            <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-white rotate-45 rounded-[1px]" />
          </motion.span>
        )}
      </AnimatePresence>

      {/* Notification dot */}
      <span className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full bg-red-500 border-2 border-[var(--color-bg)] shadow-[0_0_6px_rgba(239,68,68,0.6)]">
        <span className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-75" />
      </span>
    </motion.button>
  );
}
