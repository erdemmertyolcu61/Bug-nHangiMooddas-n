/**
 * RevenueCat entegrasyonu — native abonelik yönetimi.
 * Web'de no-op (tüm özellikler ücretsiz kalır).
 * Native'de RevenueCat SDK üzerinden StoreKit/Play Billing.
 */
import { isNative } from './native';

let _rc = null;
let _initialized = false;

const RC_API_KEY_APPLE = import.meta.env.VITE_RC_APPLE_KEY || '';
const RC_API_KEY_GOOGLE = import.meta.env.VITE_RC_GOOGLE_KEY || '';

async function getRc() {
  if (!_rc) {
    const mod = await import('@revenuecat/purchases-capacitor');
    _rc = mod.Purchases;
  }
  return _rc;
}

export async function initPurchases(userId) {
  if (!isNative || _initialized) return;
  const apiKey = RC_API_KEY_APPLE || RC_API_KEY_GOOGLE;
  if (!apiKey) return;

  try {
    const Purchases = await getRc();
    await Purchases.configure({
      apiKey,
      appUserID: userId || null,
    });
    _initialized = true;
  } catch (e) {
    console.error('[Purchases] init error:', e);
  }
}

export async function loginPurchases(userId) {
  if (!isNative || !_initialized || !userId) return;
  try {
    const Purchases = await getRc();
    await Purchases.logIn({ appUserID: String(userId) });
  } catch (e) {
    console.error('[Purchases] login error:', e);
  }
}

export async function logoutPurchases() {
  if (!isNative || !_initialized) return;
  try {
    const Purchases = await getRc();
    await Purchases.logOut();
  } catch {}
}

export async function getOfferings() {
  if (!isNative || !_initialized) return null;
  try {
    const Purchases = await getRc();
    const { offerings } = await Purchases.getOfferings();
    return offerings?.current || null;
  } catch (e) {
    console.error('[Purchases] getOfferings error:', e);
    return null;
  }
}

export async function purchasePackage(pkg) {
  if (!isNative || !_initialized || !pkg) return { ok: false };
  try {
    const Purchases = await getRc();
    const { customerInfo } = await Purchases.purchasePackage({ aPackage: pkg });
    const isPremium = customerInfo?.entitlements?.active?.premium != null;
    return { ok: true, isPremium };
  } catch (e) {
    if (e?.code === 1 || e?.message?.includes('cancelled')) {
      return { ok: false, cancelled: true };
    }
    console.error('[Purchases] purchase error:', e);
    return { ok: false, error: e?.message };
  }
}

export async function restorePurchases() {
  if (!isNative || !_initialized) return { ok: false };
  try {
    const Purchases = await getRc();
    const { customerInfo } = await Purchases.restorePurchases();
    const isPremium = customerInfo?.entitlements?.active?.premium != null;
    return { ok: true, isPremium };
  } catch (e) {
    console.error('[Purchases] restore error:', e);
    return { ok: false, error: e?.message };
  }
}

export async function checkPremium() {
  if (!isNative) return true;
  if (!_initialized) return true;
  try {
    const Purchases = await getRc();
    const { customerInfo } = await Purchases.getCustomerInfo();
    return customerInfo?.entitlements?.active?.premium != null;
  } catch {
    return true;
  }
}
