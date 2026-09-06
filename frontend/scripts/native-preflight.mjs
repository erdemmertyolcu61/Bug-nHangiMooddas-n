#!/usr/bin/env node
/**
 * Native (Capacitor) build ön-kontrolü.
 *
 * Native tarafın sinsi yanı, eksik yapılandırmanın derlemeyi BOZMAMASI: uygulama
 * kurulur, açılır, hiçbir hata vermez — sadece bildirimler hiç gelmez ya da
 * Google girişi sessizce yarıda kalır. Bu script o eksikleri build ZAMANINDA,
 * mağazaya yüklemeden önce yakalar.
 *
 * Ayrıca yapabildiği tek düzeltmeyi otomatik yapar: `GoogleService-Info.plist`
 * yerine kondu ise, içindeki REVERSED_CLIENT_ID'yi `Info.plist`'e URL şeması
 * olarak ekler (iOS Google Sign-In geri dönüşü bunsuz uygulamaya ulaşamaz).
 *
 * Kullanım:  node scripts/native-preflight.mjs [android|ios]
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');
const target = (process.argv[2] || 'all').toLowerCase();
const wantAndroid = target === 'all' || target === 'android';
const wantIos = target === 'all' || target === 'ios';

const P = {
  androidManifest: resolve(root, 'android/app/src/main/AndroidManifest.xml'),
  androidMainActivity: resolve(root, 'android/app/src/main/java/app/sinemood/MainActivity.java'),
  googleServices: resolve(root, 'android/app/google-services.json'),
  iosInfo: resolve(root, 'ios/App/App/Info.plist'),
  iosEntitlements: resolve(root, 'ios/App/App/App.entitlements'),
  iosFirebase: resolve(root, 'ios/App/App/GoogleService-Info.plist'),
};

const errors = [];
const warnings = [];
const fixes = [];
const read = (p) => (existsSync(p) ? readFileSync(p, 'utf8') : null);

// ── Otomatik düzeltme: REVERSED_CLIENT_ID → Info.plist URL şeması ────────────
function syncReversedClientId() {
  const fb = read(P.iosFirebase);
  if (!fb) return; // dosya yoksa aşağıdaki kontrol zaten hata verecek
  const m = fb.match(/<key>REVERSED_CLIENT_ID<\/key>\s*<string>([^<]+)<\/string>/);
  if (!m) {
    warnings.push(
      'GoogleService-Info.plist içinde REVERSED_CLIENT_ID yok. Firebase iOS ' +
      'uygulamasına Google Sign-In eklenmemiş olabilir — iOS girişi çalışmaz.'
    );
    return;
  }
  const scheme = m[1].trim();
  let info = read(P.iosInfo);
  if (!info) { errors.push('ios/App/App/Info.plist bulunamadı.'); return; }
  if (info.includes(`<string>${scheme}</string>`)) return; // zaten var

  // Mevcut CFBundleURLTypes dizisine yeni bir giriş ekle.
  const anchor = '<key>CFBundleURLTypes</key>\n\t<array>\n';
  if (!info.includes(anchor)) {
    errors.push(
      'Info.plist içinde CFBundleURLTypes dizisi beklenen biçimde değil; ' +
      `Google şemasını (${scheme}) elle eklemen gerekiyor.`
    );
    return;
  }
  const entry =
    '\t\t<dict>\n' +
    '\t\t\t<key>CFBundleURLName</key>\n' +
    '\t\t\t<string>google-signin</string>\n' +
    '\t\t\t<key>CFBundleURLSchemes</key>\n' +
    '\t\t\t<array>\n' +
    `\t\t\t\t<string>${scheme}</string>\n` +
    '\t\t\t</array>\n' +
    '\t\t</dict>\n';
  info = info.replace(anchor, anchor + entry);
  writeFileSync(P.iosInfo, info);
  fixes.push(`Info.plist'e Google Sign-In URL şeması eklendi (${scheme}).`);
}

// ── Kontroller ───────────────────────────────────────────────────────────────
if (wantAndroid) {
  const manifest = read(P.androidManifest);
  if (!manifest) {
    errors.push('AndroidManifest.xml yok — `npx cap add android` çalıştırıldı mı?');
  } else if (!manifest.includes('android.permission.POST_NOTIFICATIONS')) {
    errors.push(
      'AndroidManifest.xml içinde POST_NOTIFICATIONS izni yok. Android 13+ ' +
      'cihazlarda bildirimler SESSİZCE engellenir (izin diyalogu bile çıkmaz).'
    );
  }
  // `npx cap add android` MainActivity.java'yi SIFIRDAN uretir ve yazi olcegi
  // sinirini silip goturur. Kayip sessizdir: uygulama derlenir, acilir, yalniz
  // sistem yazi boyutu buyuk olan cihazlarda alt menu etiketleri kelimenin
  // ortasindan bolunur.
  const mainActivity = read(P.androidMainActivity);
  if (!mainActivity) {
    warnings.push(
      'MainActivity.java bulunamadi — Android yazi olcegi siniri yok. ' +
      'Sistem yazi boyutu %130+ olan cihazlarda alt menu etiketleri bolunur.'
    );
  } else if (!mainActivity.includes('setTextZoom')) {
    errors.push(
      'MainActivity.java icinde setTextZoom sinirlamasi yok (muhtemelen ' +
      'cap add android dosyayi yeniden uretti).\n' +
      '      Android WebView sistem yazi boyutunu web icerigine uygular; ' +
      '%130 ayarinda alt menude "MOODLAR" -> "MOODLA / R" diye bolunur.\n' +
      '      git checkout ile geri al: ' +
      'frontend/android/app/src/main/java/app/sinemood/MainActivity.java'
    );
  }

  if (!existsSync(P.googleServices)) {
    errors.push(
      'android/app/google-services.json yok → FCM çalışmaz, bildirim gitmez.\n' +
      '      Firebase Console → Proje ayarları → Android uygulaman → ' +
      '"google-services.json" indir → frontend/android/app/ içine koy.'
    );
  }
}

if (wantIos) {
  syncReversedClientId();

  const ent = read(P.iosEntitlements);
  if (!ent) {
    errors.push('ios/App/App/App.entitlements yok — `npx cap add ios` çalıştırıldı mı?');
  } else if (!ent.includes('aps-environment')) {
    errors.push(
      'App.entitlements içinde aps-environment yok → uygulama APNs kaydı ' +
      'yapamaz, TÜM iOS bildirimleri ölür.'
    );
  }
  if (!existsSync(P.iosFirebase)) {
    errors.push(
      'ios/App/App/GoogleService-Info.plist yok → FCM çalışmaz, bildirim gitmez.\n' +
      '      Firebase Console → Proje ayarları → iOS uygulaman → ' +
      '"GoogleService-Info.plist" indir → frontend/ios/App/App/ içine koy\n' +
      '      (Xcode\'da App hedefine de ekle). Sonra bu script Google Sign-In ' +
      'URL şemasını otomatik ekler.'
    );
  }
  const info = read(P.iosInfo);
  if (info && !/com\.googleusercontent\.apps\./.test(info)) {
    warnings.push(
      'Info.plist\'te Google Sign-In URL şeması (com.googleusercontent.apps.…) ' +
      'yok → iOS\'ta Google girişi geri dönüşü uygulamaya ulaşmaz. ' +
      'GoogleService-Info.plist eklenince otomatik yazılacak.'
    );
  }
}

// Native'de proxy yok: mutlak backend adresi şart.
if (!process.env.VITE_API_BASE_URL) {
  warnings.push(
    'VITE_API_BASE_URL tanımlı değil; apiConfig.js varsayılan Railway adresine ' +
    'düşecek. CI build\'inde açıkça ayarla.'
  );
}
if (!process.env.VITE_GOOGLE_CLIENT_ID) {
  warnings.push('VITE_GOOGLE_CLIENT_ID tanımlı değil → giriş butonu görünmez.');
}

// ── Rapor ────────────────────────────────────────────────────────────────────
for (const f of fixes) console.log(`\x1b[32m✔ düzeltildi:\x1b[0m ${f}`);
for (const w of warnings) console.warn(`\x1b[33m⚠ uyarı:\x1b[0m ${w}`);

if (errors.length) {
  console.error(`\n\x1b[31m✖ Native ön-kontrol başarısız (${errors.length} sorun):\x1b[0m`);
  for (const e of errors) console.error(`  • ${e}`);
  console.error(
    '\nBunlar derlemeyi bozmaz ama özelliği sessizce öldürür — ' +
    'ayrıntı için DEPLOY_CHECKLIST.md §7.\n'
  );
  process.exit(1);
}

console.log('\x1b[32m✔ Native ön-kontrol tamam.\x1b[0m');
