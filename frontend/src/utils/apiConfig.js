/**
 * API Configuration for Sinemood.
 * Web (dev): Vite proxy /api -> localhost:8002
 * Web (prod): Vercel rewrite /api -> Railway backend (same-origin)
 * Native (Capacitor): direct absolute URL to Railway backend
 */

export const DIRECT_BASE = "http://127.0.0.1:8002";

const IS_NATIVE = typeof window !== 'undefined'
  && window.Capacitor?.isNativePlatform?.();

// Web: relative path → same-origin proxy (Vercel rewrite / Vite proxy)
// Native: absolute URL → backend directly (no proxy available)
const PRODUCTION_BACKEND = (import.meta.env.VITE_API_BASE_URL
  || "https://bug-nhangimooddas-n-production.up.railway.app").replace(/\/$/, "");

export const API_BASE_URL = IS_NATIVE ? PRODUCTION_BACKEND : "";

const BACKEND_ABSOLUTE = PRODUCTION_BACKEND;

// Kanonik herkese açık FRONTEND adresi — paylaşım/QR linkleri için TEK kaynak.
// `window.location.origin` web'de doğru ama native (Capacitor) içinde
// "capacitor://localhost" döner → paylaşılan linkler bozulur. Bu sabiti
// kullanan kod hem web hem native'de doğru linki üretir. İleride özel domaine
// (ör. sinemood.app) geçişte yalnız burası / VITE_SITEMAP_HOST değişir.
export const CANONICAL_URL = (import.meta.env.VITE_SITEMAP_HOST
  || "https://bug-n-hangi-mooddas-n.vercel.app").replace(/\/$/, "");

export const getApiUrl = (path) => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`; // relative → same-origin proxy
};

/**
 * Paylaşım/OG linki üretir — MUTLAK backend URL'si döner. Bu linkler dış
 * uygulamalarda/sekmede açılır (fetch değil, navigasyon) ve backend OG meta'sını
 * sunar; o yüzden same-origin proxy'ye değil doğrudan backend'e gitmeli.
 */
export const getShareUrl = (path) => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${BACKEND_ABSOLUTE}${cleanPath}`;
};

/**
 * Avatar URL çözümleyici — /uploads veya /api ile başlayan yolları same-origin
 * proxy üzerinden (relative) döndürür. Google/harici URL'leri olduğu gibi.
 */
export const resolveAvatarUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('/uploads') || url.startsWith('/api')) {
    return `${API_BASE_URL}${url}`;
  }
  return url;
};

export const checkBackendHealth = async () => {
  try {
    const urls = [getApiUrl('/api/health'), getApiUrl('/health')];
    for (const url of urls) {
      try {
        const response = await fetch(url, { signal: AbortSignal.timeout(3000) });
        if (response.ok) {
          // healthy
          return true;
        }
      } catch {}
    }
  } catch {
    console.warn("[API] Backend unreachable at", API_BASE_URL);
  }
  return false;
};
