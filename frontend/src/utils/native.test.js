import { describe, it, expect, vi } from 'vitest';

// native.js modül düzeyinde Capacitor'ı çağırır — testte web platformu taklit et.
vi.mock('@capacitor/core', () => ({
  Capacitor: { isNativePlatform: () => false, getPlatform: () => 'web' },
}));

import { pathFromDeepLink } from './native';

describe('pathFromDeepLink', () => {
  it('universal link yolunu aynen döndürür', () => {
    expect(pathFromDeepLink('https://sinemood.app/liste/klasikler')).toBe('/liste/klasikler');
  });

  it('özel şemada ilk segmenti KAYBETMEZ', () => {
    // Regresyon: new URL('sinemood://share/123').pathname === '/123' —
    // host ('share') yolun ilk parçasıdır ve düşüyordu.
    expect(pathFromDeepLink('sinemood://share/123')).toBe('/share/123');
  });

  it('tek segmentli özel şemayı çözer', () => {
    // Regresyon: pathname boş dönüyordu → `if (path)` false → hiç gezinilmiyordu.
    expect(pathFromDeepLink('sinemood://gunun-filmi')).toBe('/gunun-filmi');
  });

  it('sorgu dizesini korur', () => {
    // Günün filmi bildirimi /gunun-filmi?mid=123 gönderir; mid düşerse
    // bildirime dokunan kullanıcı hedef filmi göremez.
    expect(pathFromDeepLink('https://sinemood.app/gunun-filmi?mid=603')).toBe('/gunun-filmi?mid=603');
    expect(pathFromDeepLink('sinemood://gunun-filmi?mid=603')).toBe('/gunun-filmi?mid=603');
  });

  it('hash parçasını korur', () => {
    expect(pathFromDeepLink('https://sinemood.app/profil#ayarlar')).toBe('/profil#ayarlar');
  });

  it('sondaki eğik çizgiyi temizler ama kökü bozmaz', () => {
    expect(pathFromDeepLink('https://sinemood.app/kesfet/')).toBe('/kesfet');
    expect(pathFromDeepLink('https://sinemood.app/')).toBe('/');
    expect(pathFromDeepLink('sinemood://')).toBe('/');
  });

  it('bozuk girdide boş döner (çökme yok)', () => {
    expect(pathFromDeepLink('bu bir url degil')).toBe('');
    expect(pathFromDeepLink('')).toBe('');
    expect(pathFromDeepLink(null)).toBe('');
  });

  it('sonuç her zaman eğik çizgiyle başlar', () => {
    for (const u of [
      'https://sinemood.app/a/b',
      'sinemood://a/b',
      'sinemood://a',
      'https://sinemood.app/',
    ]) {
      expect(pathFromDeepLink(u).startsWith('/')).toBe(true);
    }
  });
});
