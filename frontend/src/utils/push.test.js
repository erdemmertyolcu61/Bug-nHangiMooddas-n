import { describe, it, expect, vi, beforeEach } from 'vitest';

// ── Mock'lar ───────────────────────────────────────────────────────────────
// push.js modül düzeyinde `isNative`i okuyor; native davranışı test etmek için
// native.js'i komple taklit ediyoruz (Capacitor'a hiç dokunmadan).
vi.mock('./native', () => ({ isNative: true, platform: 'android' }));

const api = vi.hoisted(() => ({
  subscribePush: vi.fn().mockResolvedValue({ ok: true }),
  unsubscribePush: vi.fn().mockResolvedValue({ ok: true }),
  getPushPublicKey: vi.fn().mockResolvedValue({ enabled: false, public_key: '' }),
}));
vi.mock('../services/api', () => api);

const fm = vi.hoisted(() => ({
  checkPermissions: vi.fn(),
  requestPermissions: vi.fn(),
  getToken: vi.fn(),
  deleteToken: vi.fn().mockResolvedValue(undefined),
  addListener: vi.fn(),
}));
vi.mock('@capacitor-firebase/messaging', () => ({ FirebaseMessaging: fm }));

import {
  isPushSubscribed, ensureNativePushRegistered, enablePush, disablePush,
} from './push';

beforeEach(() => {
  vi.clearAllMocks();
  fm.deleteToken.mockResolvedValue(undefined);
});

describe('isPushSubscribed (native)', () => {
  it('izin verilmiş AMA jeton yoksa "abone" demez', async () => {
    // Regresyon: eskiden yalnız checkPermissions()'a bakılıyordu. Android
    // 13+'ta izin bir kez verilince hep "granted" döner; arayüz anahtarı AÇIK
    // gösterip kullanıcıyı hiç dokundurmuyor, dolayısıyla subscribePush() hiç
    // çağrılmıyor ve sunucuda jeton olmuyordu → tek bildirim gelmiyordu.
    fm.checkPermissions.mockResolvedValue({ receive: 'granted' });
    fm.getToken.mockResolvedValue({ token: '' });
    expect(await isPushSubscribed()).toBe(false);
  });

  it('izin + jeton varsa abone sayar', async () => {
    fm.checkPermissions.mockResolvedValue({ receive: 'granted' });
    fm.getToken.mockResolvedValue({ token: 'fcm-abc' });
    expect(await isPushSubscribed()).toBe(true);
  });

  it('izin yoksa jetonu hiç sormaz', async () => {
    fm.checkPermissions.mockResolvedValue({ receive: 'denied' });
    expect(await isPushSubscribed()).toBe(false);
    expect(fm.getToken).not.toHaveBeenCalled();
  });

  it('Firebase yapılandırması yoksa çökmez, false döner', async () => {
    fm.checkPermissions.mockRejectedValue(new Error('Default FirebaseApp is not initialized'));
    expect(await isPushSubscribed()).toBe(false);
  });
});

describe('ensureNativePushRegistered', () => {
  it('izin zaten verilmişse jetonu sunucuya sessizce yazar', async () => {
    fm.checkPermissions.mockResolvedValue({ receive: 'granted' });
    fm.getToken.mockResolvedValue({ token: 'fcm-xyz' });
    const r = await ensureNativePushRegistered();
    expect(r.ok).toBe(true);
    expect(api.subscribePush).toHaveBeenCalledWith({
      endpoint: 'fcm-xyz', type: 'fcm', is_pwa: false,
    });
  });

  it('izin verilmemişse sunucuya hiçbir şey yazmaz (izin diyalogu da açmaz)', async () => {
    fm.checkPermissions.mockResolvedValue({ receive: 'prompt' });
    const r = await ensureNativePushRegistered();
    expect(r).toEqual({ ok: false, reason: 'not-granted' });
    expect(api.subscribePush).not.toHaveBeenCalled();
    expect(fm.requestPermissions).not.toHaveBeenCalled();
  });

  it('Firebase yapılandırması eksikse sebebi ayırt eder', async () => {
    fm.checkPermissions.mockResolvedValue({ receive: 'granted' });
    fm.getToken.mockRejectedValue(new Error('Default FirebaseApp is not initialized in this process'));
    const r = await ensureNativePushRegistered();
    expect(r).toEqual({ ok: false, reason: 'no-firebase-config' });
  });
});

describe('enablePush (native)', () => {
  it('başarılı akışta jetonu kaydeder ve tokenRefresh dinleyicisini bağlar', async () => {
    fm.requestPermissions.mockResolvedValue({ receive: 'granted' });
    fm.getToken.mockResolvedValue({ token: 'fcm-1' });
    const r = await enablePush();
    expect(r).toEqual({ ok: true });
    expect(api.subscribePush).toHaveBeenCalledWith({
      endpoint: 'fcm-1', type: 'fcm', is_pwa: false,
    });
  });

  it('tokenRefresh dinleyicisi tekrar tekrar bağlanmaz', async () => {
    fm.requestPermissions.mockResolvedValue({ receive: 'granted' });
    fm.getToken.mockResolvedValue({ token: 'fcm-1' });
    await enablePush();
    await enablePush();
    await enablePush();
    const refreshBinds = fm.addListener.mock.calls.filter(([e]) => e === 'tokenRefresh');
    expect(refreshBinds.length).toBeLessThanOrEqual(1);
  });

  it('izin reddedilirse "denied" döner', async () => {
    fm.requestPermissions.mockResolvedValue({ receive: 'denied' });
    expect(await enablePush()).toEqual({ ok: false, reason: 'denied' });
    expect(api.subscribePush).not.toHaveBeenCalled();
  });

  it('yapılandırma hatasını "error" değil "no-firebase-config" olarak bildirir', async () => {
    // Kullanıcıya "tekrar dene" demek yanlış: tekrar denemek asla çözmez.
    fm.requestPermissions.mockRejectedValue(new Error('Default FirebaseApp is not initialized'));
    expect(await enablePush()).toEqual({ ok: false, reason: 'no-firebase-config' });
  });

  it('eklenti derlemede yoksa "plugin-missing" der', async () => {
    fm.requestPermissions.mockRejectedValue(new Error('UNIMPLEMENTED'));
    expect(await enablePush()).toEqual({ ok: false, reason: 'plugin-missing' });
  });
});

describe('disablePush (native)', () => {
  it('jetonu ÖNCE sunucudan siler, sonra cihazdan', async () => {
    // Regresyon: yalnız deleteToken() çağrılıyordu. Jeton sunucuda ölü kalıyor,
    // kullanıcı bildirimi kapatmış olmasına rağmen her günlük push o kayda
    // gitmeye devam ediyordu.
    const order = [];
    fm.getToken.mockResolvedValue({ token: 'fcm-sil' });
    api.unsubscribePush.mockImplementation(async () => { order.push('sunucu'); return { ok: true }; });
    fm.deleteToken.mockImplementation(async () => { order.push('cihaz'); });

    const r = await disablePush();
    expect(r).toEqual({ ok: true });
    expect(api.unsubscribePush).toHaveBeenCalledWith('fcm-sil');
    expect(order).toEqual(['sunucu', 'cihaz']);
  });

  it('jeton okunamasa bile cihazdan silmeyi dener', async () => {
    fm.getToken.mockRejectedValue(new Error('no token'));
    const r = await disablePush();
    expect(r).toEqual({ ok: true });
    expect(fm.deleteToken).toHaveBeenCalled();
  });
});
