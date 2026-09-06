import { Capacitor } from '@capacitor/core';

export const isNative = Capacitor.isNativePlatform();
export const platform = Capacitor.getPlatform(); // 'ios' | 'android' | 'web'

let initialized = false;

export async function initNativePlugins() {
  if (!isNative || initialized) return;
  initialized = true;

  const { SplashScreen } = await import('@capacitor/splash-screen');
  const { StatusBar, Style } = await import('@capacitor/status-bar');
  const { Keyboard } = await import('@capacitor/keyboard');
  const { App } = await import('@capacitor/app');

  StatusBar.setStyle({ style: Style.Dark }).catch(() => {});
  StatusBar.setBackgroundColor({ color: '#000000' }).catch(() => {});

  Keyboard.setAccessoryBarVisible({ isVisible: true }).catch(() => {});

  // Hide splash after app is mounted
  SplashScreen.hide({ fadeOutDuration: 300 }).catch(() => {});

  // Handle Android back button
  App.addListener('backButton', ({ canGoBack }) => {
    if (canGoBack) {
      window.history.back();
    } else {
      App.minimizeApp();
    }
  });

  // Handle deep links
  App.addListener('appUrlOpen', ({ url }) => {
    navigateToPath(pathFromDeepLink(url));
  });

  // Bildirime dokunma (FCM). Backend her push'a data.url koyuyor ama native
  // tarafta hiçbir dinleyici yoktu: bildirime dokunmak uygulamayı yalnızca
  // ana ekranda açıyor, hedef sayfa yok sayılıyordu. (Web'de bunu
  // public/push-sw.js'teki notificationclick zaten yapıyor.)
  try {
    const { FirebaseMessaging } = await import('@capacitor-firebase/messaging');
    FirebaseMessaging.addListener('notificationActionPerformed', (event) => {
      const url = event?.notification?.data?.url;
      if (url) navigateToPath(url);
    });
  } catch {
    // Plugin yoksa (ör. eski build) sessizce geç — uygulama çalışmaya devam etsin.
  }
}

/**
 * Derin bağlantıdan uygulama içi yolu çıkarır.
 *
 * İki farklı biçim gelir ve `new URL(...).pathname` ikisinde de doğru sonuç
 * VERMEZ:
 *   - Universal link  → https://alanadi/liste/klasikler   (pathname doğru)
 *   - Özel şema       → sinemood://gunun-filmi            (host = ilk segment!)
 * Özel şemada `pathname` ya boş kalıyor ya da ilk segmenti düşürüyordu
 * (`sinemood://share/123` → "/123"), yani bağlantı ya hiç çalışmıyor ya da
 * yanlış sayfaya gidiyordu. Sorgu dizesi de tamamen atılıyordu — günün filmi
 * bildirimi `/gunun-filmi?mid=123` gönderdiği için hedef film kayboluyordu.
 */
export function pathFromDeepLink(rawUrl) {
  try {
    const u = new URL(rawUrl);
    const isHttp = u.protocol === 'http:' || u.protocol === 'https:';
    // Özel şemada host aslında yolun ilk parçasıdır.
    const base = isHttp ? u.pathname : `/${u.host}${u.pathname}`;
    const path = base.replace(/\/{2,}/g, '/').replace(/\/$/, '') || '/';
    return `${path}${u.search}${u.hash}`;
  } catch {
    return '';
  }
}

/** SPA içi gezinme — React Router popstate ile yakalar. */
function navigateToPath(pathWithQuery) {
  if (!pathWithQuery) return;
  const path = pathWithQuery.startsWith('/') ? pathWithQuery : `/${pathWithQuery}`;
  window.history.pushState(null, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
}
