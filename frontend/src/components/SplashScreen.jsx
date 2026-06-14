import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/* ═══════════════════════════════════════════════════════════════════
   SplashScreen — Cinematic Spotlight Animasyonu
   Storyboard:
     01  Zifiri karanlık zemin.
     02  Işık hüzmesi (spotlight) ve parlayan amber orb yavaşça belirir.
     03  Film Makarası (Lottie) bir "logo" edasıyla altın gibi parlayarak döner.
     04  SİNEMOOD yazısı bulanıklıktan (blur) netliğe doğru süzülür, harf aralıkları genişler.
     05  "bugün hangi mooddasın?" sloganı alttan fade-in olur.
     06  Framer Motion exit ile soft fade-out.
   ═══════════════════════════════════════════════════════════════════ */

const SPLASH_KEY = 'fc_splash_cinematic_v2';
const SHOW_MS = 4200; // Animasyonun tadını çıkarmak için biraz uzatıldı

export default function SplashScreen() {
  const [show, setShow] = useState(() => {
    if (sessionStorage.getItem(SPLASH_KEY)) return false;
    sessionStorage.setItem(SPLASH_KEY, '1');
    return true;
  });

  useEffect(() => {
    if (!show) return;
    const timer = setTimeout(() => setShow(false), SHOW_MS);
    return () => clearTimeout(timer);
  }, [show]);

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          key="splash-cinematic"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.8, ease: [0.25, 1, 0.5, 1] }}
          className="fixed inset-0 z-[9999] flex flex-col items-center justify-center overflow-hidden"
          style={{ backgroundColor: '#050302' }} // Çok koyu amber/siyah
        >
          {/* Spotlight / Işık Hüzmesi */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: '-20%' }}
            animate={{ opacity: 1, scale: 1, y: '0%' }}
            transition={{ duration: 2.5, ease: "easeOut" }}
            className="absolute top-0 left-1/2 -translate-x-1/2 w-[200vw] sm:w-[150vw] h-[150vh] pointer-events-none"
            style={{
              background: 'radial-gradient(ellipse at 50% 20%, rgba(255, 191, 0, 0.12) 0%, rgba(255, 150, 50, 0.03) 40%, transparent 70%)',
              filter: 'blur(30px)',
              mixBlendMode: 'screen'
            }}
          />

          {/* Işık Kaynağı (Glowing Orb) */}
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: [0, 0.6, 0.3], scale: [0, 1.5, 1.2] }}
            transition={{ duration: 3, ease: "easeInOut" }}
            className="absolute top-[35%] left-1/2 -translate-x-1/2 w-[40vmin] h-[40vmin] rounded-full blur-[60px] pointer-events-none"
            style={{ background: 'rgba(255, 191, 0, 0.15)', mixBlendMode: 'screen' }}
          />

          {/* İçerik Konteyneri */}
          <div className="relative z-10 flex flex-col items-center mt-[-5vh]">
            
            {/* SİNEMOOD Logo Yazısı */}
            <motion.h1
              initial={{ filter: 'blur(20px)', opacity: 0, letterSpacing: '0.05em', scale: 0.9 }}
              animate={{ filter: 'blur(0px)', opacity: 1, letterSpacing: '0.35em', scale: 1 }}
              transition={{ duration: 2, ease: [0.16, 1, 0.3, 1], delay: 0.3 }}
              className="font-serif font-bold text-transparent bg-clip-text select-none text-center"
              style={{
                fontSize: 'clamp(32px, 8vmin, 64px)',
                backgroundImage: 'linear-gradient(180deg, #ffffff 0%, #ffdf99 45%, #e6a83a 100%)',
                paddingLeft: '0.35em', // letter-spacing dengesi
                textShadow: '0px 8px 30px rgba(255, 191, 0, 0.4)',
                WebkitFontSmoothing: 'antialiased'
              }}
            >
              SINEMOOD
            </motion.h1>

            {/* Slogan */}
            <motion.p
              initial={{ opacity: 0, y: 15, filter: 'blur(5px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              transition={{ duration: 1.2, ease: "easeOut", delay: 1.5 }}
              className="mt-6 font-serif italic text-amber-100/60 tracking-[0.25em] uppercase text-[10px] sm:text-[11px] select-none text-center"
              style={{ textShadow: '0px 2px 10px rgba(255, 191, 0, 0.2)' }}
            >
              bugün hangi mooddasın?
            </motion.p>
          </div>

          {/* Sinematik Toz / Film Grain Overlay */}
          <div 
            className="absolute inset-0 pointer-events-none opacity-[0.04] mix-blend-overlay"
            style={{ backgroundImage: "url('data:image/svg+xml;utf8,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence baseFrequency=%220.8%22 numOctaves=%222%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23n)%22 opacity=%220.7%22/%3E%3C/svg%3E')" }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
