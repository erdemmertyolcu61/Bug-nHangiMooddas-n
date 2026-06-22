import { useEffect, useRef, useState, useCallback } from 'react';
import { useTheme } from '../context/ThemeContext';
import { isNative } from '../utils/native';

function NativeGoogleButton({ clientId, onCredential }) {
  const [loading, setLoading] = useState(false);

  const handleNativeSignIn = useCallback(async () => {
    if (loading) return;
    setLoading(true);
    try {
      const { GoogleAuth } = await import('@codetrix-studio/capacitor-google-auth');
      await GoogleAuth.initialize({
        clientId,
        scopes: ['profile', 'email'],
        grantOfflineAccess: false,
      });
      const result = await GoogleAuth.signIn();
      if (result?.authentication?.idToken) {
        onCredential(result.authentication.idToken);
      }
    } catch (e) {
      if (e?.message !== 'The user canceled the sign-in flow.') {
        console.error('[GoogleSignIn] native error:', e);
      }
    } finally {
      setLoading(false);
    }
  }, [clientId, onCredential, loading]);

  return (
    <button
      onClick={handleNativeSignIn}
      disabled={loading}
      className="flex items-center justify-center gap-3 w-[280px] h-[44px] rounded-full
                 bg-white border border-white/20 shadow-sm
                 text-[14px] font-medium text-gray-700
                 disabled:opacity-50 transition-all active:scale-[0.98]"
    >
      <svg width="20" height="20" viewBox="0 0 24 24">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
      </svg>
      {loading ? 'Giriş yapılıyor...' : 'Google ile giriş yap'}
    </button>
  );
}

function WebGoogleButton({ clientId, onCredential, width }) {
  const holderRef = useRef(null);
  const { theme } = useTheme();
  const gsiTheme = theme === 'light' ? 'outline' : 'filled_black';

  useEffect(() => {
    if (!clientId || !holderRef.current) return;
    let cancelled = false;
    let pollId;

    const tryInit = () => {
      if (cancelled) return;
      const gsi = window.google?.accounts?.id;
      if (!gsi) {
        pollId = setTimeout(tryInit, 250);
        return;
      }
      try {
        gsi.initialize({
          client_id: clientId,
          callback: (resp) => {
            if (resp?.credential) onCredential(resp.credential);
          },
          auto_select: false,
          cancel_on_tap_outside: true,
        });
        if (holderRef.current) {
          holderRef.current.innerHTML = '';
          gsi.renderButton(holderRef.current, {
            type: 'standard',
            theme: gsiTheme,
            text: 'signin_with',
            shape: 'pill',
            locale: 'tr',
            width,
          });
        }
      } catch (e) {
        console.error('[GoogleSignIn] init error:', e);
      }
    };

    tryInit();
    return () => {
      cancelled = true;
      if (pollId) clearTimeout(pollId);
    };
  }, [clientId, onCredential, width, gsiTheme]);

  return <div ref={holderRef} className="flex justify-center min-h-[44px]" />;
}

export default function GoogleSignInButton({ clientId, onCredential, width = 280 }) {
  if (isNative) {
    return <NativeGoogleButton clientId={clientId} onCredential={onCredential} />;
  }
  return <WebGoogleButton clientId={clientId} onCredential={onCredential} width={width} />;
}
