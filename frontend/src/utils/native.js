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
    const path = new URL(url).pathname;
    if (path) {
      window.location.hash = '';
      window.history.pushState(null, '', path);
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  });
}
