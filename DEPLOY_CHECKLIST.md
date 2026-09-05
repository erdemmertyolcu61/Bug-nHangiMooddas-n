# Sinemood — Lansman (Go-Live) Kontrol Listesi

Bu liste, sistemi canlıya alırken Render (veya benzeri) ortamında yapılması gereken
**ayar/ops** adımlarını içerir. Kod tarafı hazırdır; aşağıdakiler senin elinle yapılır.

## 1. Backend env (film-connoisseur-api — FastAPI servisi)
- [ ] **`JWT_SECRET`** — güçlü, sabit bir değer ata (örn. `openssl rand -hex 32`).
      ⚠️ **`ENVIRONMENT=production` iken bu değişken yoksa backend hiç açılmaz**
      (`config.py` `RuntimeError` fırlatır) — sessizce rastgele anahtar üretilmez.
      Dev'de yoksa oturumluk rastgele anahtar üretilir (token'lar restart'ta düşer).
- [ ] **`BETA_PASSWORD`** — **boş bırak / tanımlama** → beta kapısı kapanır, site herkese açılır.
      (Dolu olursa tüm organik ziyaretçiler şifre ekranına takılır.)
- [ ] **`ALLOWED_ORIGINS`** — güncel frontend domain'ini içermeli. ŞU AN canlı domain
      `https://bug-n-hangi-mooddas-n.vercel.app` (Vercel) ve `backend/config.py` default'unda
      zaten var. Yalnızca özel alan adına (ör. `sinemood.app`) geçince güncelle.
- [ ] **`FRONTEND_BASE_URL`** = `https://bug-n-hangi-mooddas-n.vercel.app` (veya bağladığın
      özel alan adı). OG/paylaşım kartları ve referral linkleri bunu kullanır.
- [ ] **API anahtarları** tanımlı mı: `TMDB_API_KEY`, `OMDB_API_KEY`, `ANTHROPIC_API_KEY`,
      `GEMINI_API_KEY`.
- [ ] **`ADMIN_PASSWORD`** — günlük push / yönetim uçları için güçlü bir değer ata.
      Boş bırakılırsa admin uçları **kapalı** kalır (403 — güvenli varsayılan).
      Teşhis ucu `/api/diag` de admin korumalıdır: `X-Admin-Password: <ADMIN_PASSWORD>`.
- [ ] (Kalıcı veri istiyorsan) **Turso** env'leri (libsql URL + token) — yoksa lokal SQLite kullanılır.
- [ ] **Bildirim kanalları — en az biri gerekli, yoksa hiçbir planlı bildirim gitmez:**
      - *Web push (tarayıcı/PWA):* `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT`
        → `npx web-push generate-vapid-keys` ile üret.
      - *Native push (iOS/Android uygulama):* Firebase servis hesabı →
        `GOOGLE_APPLICATION_CREDENTIALS` (JSON dosya yolu) **veya** `FIREBASE_CONFIG` (gömülü JSON).
      ℹ️ İkisi bağımsızdır: VAPID olmadan da native bildirimler çalışır. Hiçbiri yoksa
      push sessizce no-op'tur (uygulama bozulmaz, sadece bildirim gitmez).
- [ ] **Bildirim duman testi:** `GET /api/admin/push-debug/<user_id>` (header
      `X-Admin-Password`) → `push_configured: true` ve her abonelik için
      `test_result: "ok"` dönmeli. `sub_type` alanı kanalı (`vapid`/`fcm`) gösterir.

## 2. Frontend env (film-connoisseur — STATIC site)
- [ ] **`VITE_GOOGLE_CLIENT_ID`** — Google girişi için (boşsa giriş butonu çıkmaz).
- [ ] **`VITE_API_BASE_URL`** — backend API adresi.
- [ ] **`VITE_SITEMAP_HOST`** — (opsiyonel) sitemap/canonical host'u; varsayılan `https://sinemood.onrender.com`.
- [ ] **Analytics (opsiyonel, gizlilik-dostu):** `VITE_ANALYTICS_PROVIDER` (`umami`|`plausible`),
      `VITE_ANALYTICS_SRC`, `VITE_ANALYTICS_SITE_ID` (umami) / `VITE_ANALYTICS_DOMAIN` (plausible).
      Analytics yalnız kullanıcı **onay** verdiğinde (ConsentBanner) çalışır.

## 3. SEO
- [x] `public/robots.txt` + build'de üretilen `public/sitemap.xml` (prebuild script).
- [x] Sayfa-başı `<title>` / `description` / `canonical` (useDocumentMeta).
- [ ] Google Search Console'a domaini ekle, `sitemap.xml`'i gönder.
- [ ] (P1) Mood/landing sayfaları için prerender/SSR ile gerçek içerik indeksleme.

## 4. Retention / İçerik
- [ ] **Günlük push cron'u:** harici bir cron (örn. cron-job.org) ile günde 1 kez
      `POST https://<api-host>/api/admin/daily-push`, header: `X-Admin-Password: <ADMIN_PASSWORD>`.
- [ ] (Opsiyonel) Web push'u aktifleştirmek için VAPID anahtarlarını gir (madde 1).

## 5. Güvenilirlik
- [ ] **Cold-start:** Render free tier ~30sn uyanma yaşatır. Keep-alive cron
      (her ~10 dk `GET /api/health`) ekle veya ücretli tier'a geç.
- [ ] **Hata izleme (önerilir, P1):** Sentry (FE + BE) DSN ekle — prod hataları görünür olsun.

## 6. Yayın öncesi duman testi (smoke)
- [ ] Ana sayfa → mood seç → Discover akışı çalışıyor.
- [ ] Sürpriz Film, Kafan Mı Karışık, Listeler, Arama açılıyor.
- [ ] Google ile giriş + profil + watchlist senkron.
- [ ] **Misafir veri izolasyonu:** iki ayrı tarayıcıda (giriş YAPMADAN) farklı filmler
      kaydet → biri diğerinin Defterim'inde görünmemeli. (Misafir verisi yalnız
      localStorage'da tutulur; sunucuda ortak `user_id=0` kovası kullanılmaz.)
- [ ] Paylaşım linkleri (`/share/u/<kullanıcı>`, `/share/<film_id>`) crawler'a doğru OG kartı veriyor
      (`curl -A "facebookexternalhit" ...`).
- [ ] `robots.txt` ve `sitemap.xml` canlıda erişilebilir; sitemap doğru host'u gösteriyor.
- [ ] Gizlilik sayfası (`/gizlilik`) ve Kullanım Koşulları (`/kosullar`) açılıyor;
      ikisi de Profil → Ayarlar içinden erişilebiliyor. ConsentBanner ilk ziyarette çıkıyor.
- [ ] **Bildirim akışı:** izin ver → zil toggle'ı "açık" → Ayarlar'da "Günlük Film Saati"
      görünüyor → saat değiştir → `GET /api/push/notify-time` yeni saati dönüyor.
      İkinci cihazdan abone ol → aynı saati devralmalı (iki farklı saatte iki push GELMEMELİ).
- [ ] **Verilerim:** Profil → Ayarlar → "Verilerim" indirilen JSON'da `eksik_bolumler: []`
      ve izleme listesi dışındaki bölümler (notlar, sözler, listeler) de dolu.
- [ ] Hem Espresso hem Latte temasında görsel/okunabilirlik kontrolü.

## 7. Yasal — mağaza başvurusundan ÖNCE
- [ ] **Veri sorumlusu kimliği (KVKK md. 10):** `frontend/src/pages/Gizlilik.jsx` §1'de
      şu an yalnızca "Sinemood" yazıyor. Kanun, veri sorumlusunun **gerçek kimliğini**
      (şahıs adı veya şirket unvanı + adres) şart koşar. Yayından önce doldur.
- [ ] **E-posta adresleri canlı olmalı:** `privacy@sinemood.app` (gizlilik talepleri,
      30 gün içinde yanıt zorunlu) ve `destek@sinemood.app` (içerik bildirimleri).
      Apple, UGC uygulamalarında çalışan bir iletişim kanalı arar.
- [ ] **App Store Connect / Play Console alanları:**
      - Privacy Policy URL → `https://<domain>/gizlilik`
      - Terms of Use (EULA) URL → `https://<domain>/kosullar`
      - Play "Data safety" formu: toplanan veriler Gizlilik metni §2 ile birebir eşleşmeli
        (hesap bilgisi, uygulama içi içerik, cihaz bildirim jetonu, abonelik durumu).
- [ ] **Yaş derecelendirmesi:** metinlerde 13+ taahhüt ediliyor; mağaza derecelendirme
      anketini UGC + sosyal etkileşim içerecek şekilde doldur (13 altına işaretleme).
- [ ] **UGC moderasyon taahhüdü (App Store 1.2):** Koşullar §4 bildirimlerin **24 saat**
      içinde inceleneceğini yazıyor. `/api/admin/reports` kuyruğunu günlük takip edecek
      bir sahip belirle — taahhüt yazılı, uygulanmazsa mağaza şikâyeti doğar.
- [ ] **Abonelik metinleri (App Store 3.1.2):** satın alma ekranında fiyat, dönem ve
      otomatik yenileme açıkça yazmalı; Koşullar §5 ile tutarlı olmalı.
