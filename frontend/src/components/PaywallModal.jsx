import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Crown, Check, Loader2, RotateCcw } from 'lucide-react';
import { getOfferings, purchasePackage, restorePurchases } from '../utils/purchases';
import { isNative } from '../utils/native';

const FEATURES = [
  'Reklamsız deneyim',
  'Sınırsız film önerisi',
  'Özel mood analizleri',
  'Premium rozetler',
  'Erken erişim özellikler',
];

export default function PaywallModal({ onClose, onSubscribed }) {
  const [offering, setOffering] = useState(null);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState(null);
  const [restoring, setRestoring] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const o = await getOfferings();
      if (!cancelled) {
        setOffering(o);
        setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const handlePurchase = useCallback(async (pkg) => {
    setBuying(pkg.identifier);
    setError('');
    const result = await purchasePackage(pkg);
    setBuying(null);
    if (result.ok && result.isPremium) {
      onSubscribed?.();
      onClose();
    } else if (!result.cancelled) {
      setError(result.error || 'Satın alma başarısız oldu.');
    }
  }, [onClose, onSubscribed]);

  const handleRestore = useCallback(async () => {
    setRestoring(true);
    setError('');
    const result = await restorePurchases();
    setRestoring(false);
    if (result.ok && result.isPremium) {
      onSubscribed?.();
      onClose();
    } else {
      setError('Geri yüklenecek satın alma bulunamadı.');
    }
  }, [onClose, onSubscribed]);

  if (!isNative) return null;

  const packages = offering?.availablePackages || [];

  return (
    <AnimatePresence>
      <motion.div className="fixed inset-0 z-[1000] bg-black/80 backdrop-blur-sm"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} />
      <motion.div
        className="fixed inset-x-0 bottom-0 z-[1001] max-h-[92vh] flex flex-col
                   bg-gradient-to-b from-[#1a1200] to-[#161010] border-t border-amber-500/30
                   rounded-t-[2rem] shadow-[0_-20px_60px_rgba(0,0,0,0.7)] pb-safe overflow-y-auto"
        initial={{ y: '100%' }} animate={{ y: 0 }} exit={{ y: '100%' }}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Handle bar */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 rounded-full bg-white/20" />
        </div>

        {/* Close */}
        <button onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors z-10">
          <X size={18} className="text-white/70" />
        </button>

        {/* Header */}
        <div className="flex flex-col items-center px-6 pt-4 pb-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-400 to-amber-600
                          flex items-center justify-center mb-4 shadow-lg shadow-amber-500/30">
            <Crown size={32} className="text-black" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-1">Sinemood Premium</h2>
          <p className="text-white/50 text-sm text-center">Film deneyimini bir üst seviyeye taşı</p>
        </div>

        {/* Features */}
        <div className="px-6 pb-6 space-y-3">
          {FEATURES.map((f) => (
            <div key={f} className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <Check size={14} className="text-amber-400" />
              </div>
              <span className="text-white/80 text-sm">{f}</span>
            </div>
          ))}
        </div>

        {/* Packages */}
        <div className="px-6 pb-4 space-y-3">
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 size={24} className="text-amber-400 animate-spin" />
            </div>
          ) : packages.length === 0 ? (
            <p className="text-center text-white/40 text-sm py-4">
              Şu an kullanılabilir plan yok.
            </p>
          ) : (
            packages.map((pkg) => {
              const product = pkg.product;
              const isBuying = buying === pkg.identifier;
              return (
                <button key={pkg.identifier} onClick={() => handlePurchase(pkg)}
                  disabled={!!buying}
                  className="w-full flex items-center justify-between p-4 rounded-2xl
                             bg-white/5 border border-white/10 hover:border-amber-500/40
                             transition-all disabled:opacity-50">
                  <div className="text-left">
                    <div className="text-white font-semibold text-sm">{product?.title || pkg.identifier}</div>
                    <div className="text-white/40 text-xs mt-0.5">{product?.description || ''}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isBuying ? (
                      <Loader2 size={18} className="text-amber-400 animate-spin" />
                    ) : (
                      <span className="text-amber-400 font-bold text-sm">
                        {product?.priceString || ''}
                      </span>
                    )}
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Error */}
        {error && (
          <p className="px-6 pb-3 text-red-400 text-xs text-center">{error}</p>
        )}

        {/* Restore */}
        <div className="px-6 pb-8 flex justify-center">
          <button onClick={handleRestore} disabled={restoring || !!buying}
            className="flex items-center gap-1.5 text-white/40 hover:text-white/60 text-xs
                       transition-colors disabled:opacity-50">
            {restoring ? <Loader2 size={14} className="animate-spin" /> : <RotateCcw size={14} />}
            Satın alımları geri yükle
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
