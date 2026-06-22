/**
 * Push notification helpers — web (VAPID) + native (FCM via Capacitor).
 * Platform detection happens automatically; callers use the same API.
 */
import { getPushPublicKey, subscribePush, unsubscribePush } from '../services/api';
import { isNative } from './native';

// ═══════════════════════════════════════════
// Web Push (VAPID)
// ═══════════════════════════════════════════

function webPushSupported() {
  return typeof window !== 'undefined' &&
    'serviceWorker' in navigator &&
    'PushManager' in window &&
    'Notification' in window;
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base64);
  const arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
  return arr;
}

async function getRegistration() {
  if (!('serviceWorker' in navigator)) return null;
  return (await navigator.serviceWorker.getRegistration()) || (await navigator.serviceWorker.ready);
}

function isStandalone() {
  return window.matchMedia('(display-mode: standalone)').matches
    || window.navigator.standalone
    || false;
}

// ═══════════════════════════════════════════
// Native Push (FCM via @capacitor-firebase/messaging)
// ═══════════════════════════════════════════

let _firebaseMessaging = null;
async function getFirebaseMessaging() {
  if (!_firebaseMessaging) {
    const mod = await import('@capacitor-firebase/messaging');
    _firebaseMessaging = mod.FirebaseMessaging;
  }
  return _firebaseMessaging;
}

// ═══════════════════════════════════════════
// Public API (platform-agnostic)
// ═══════════════════════════════════════════

export function pushSupported() {
  if (isNative) return true;
  return webPushSupported();
}

export async function isPushSubscribed() {
  if (isNative) {
    try {
      const fm = await getFirebaseMessaging();
      const { receive } = await fm.checkPermissions();
      return receive === 'granted';
    } catch { return false; }
  }
  if (!webPushSupported() || Notification.permission !== 'granted') return false;
  try {
    const reg = await getRegistration();
    if (!reg) return false;
    const sub = await reg.pushManager.getSubscription();
    return !!sub;
  } catch { return false; }
}

export async function isPushEnabledOnServer() {
  if (isNative) return true;
  try {
    const { enabled } = await getPushPublicKey();
    return !!enabled;
  } catch { return false; }
}

export async function enablePush() {
  if (isNative) {
    try {
      const fm = await getFirebaseMessaging();
      const { receive } = await fm.requestPermissions();
      if (receive !== 'granted') return { ok: false, reason: 'denied' };
      const { token } = await fm.getToken();
      if (!token) return { ok: false, reason: 'no-token' };
      await subscribePush({ endpoint: token, type: 'fcm', is_pwa: false });

      fm.addListener('tokenRefresh', async ({ token: newToken }) => {
        await subscribePush({ endpoint: newToken, type: 'fcm', is_pwa: false }).catch(() => {});
      });

      return { ok: true };
    } catch (e) {
      console.error('[Push] native enable error:', e);
      return { ok: false, reason: 'error' };
    }
  }

  // Web VAPID flow
  if (!webPushSupported()) return { ok: false, reason: 'unsupported' };
  const { enabled, public_key } = await getPushPublicKey();
  if (!enabled || !public_key) return { ok: false, reason: 'disabled' };

  const perm = await Notification.requestPermission();
  if (perm !== 'granted') return { ok: false, reason: 'denied' };

  const reg = await getRegistration();
  if (!reg) return { ok: false, reason: 'no-sw' };

  let sub = await reg.pushManager.getSubscription();
  if (!sub) {
    sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(public_key),
    });
  }
  await subscribePush({ ...sub.toJSON(), is_pwa: isStandalone() });
  return { ok: true };
}

export async function disablePush() {
  if (isNative) {
    try {
      const fm = await getFirebaseMessaging();
      await fm.deleteToken();
      return { ok: true };
    } catch { return { ok: false }; }
  }

  if (!webPushSupported()) return { ok: false };
  try {
    const reg = await getRegistration();
    if (!reg) return { ok: false };
    const sub = await reg.pushManager.getSubscription();
    if (sub) {
      await unsubscribePush(sub.endpoint).catch(() => {});
      await sub.unsubscribe().catch(() => {});
    }
    return { ok: true };
  } catch { return { ok: false }; }
}
