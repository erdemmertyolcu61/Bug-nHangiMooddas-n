import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import useDocumentMeta from '../utils/useDocumentMeta';
import { hasAnalyticsConsent, grantAnalyticsConsent, revokeAnalyticsConsent } from '../utils/analytics';

/**
 * Gizlilik & KVKK Aydınlatma Metni.
 * Hangi veriler, neden işleniyor, kullanıcı hakları + iletişim.
 */
export default function Gizlilik() {
  const navigate = useNavigate();
  const [analyticsOn, setAnalyticsOn] = useState(() => hasAnalyticsConsent());
  const toggleAnalytics = () => {
    if (analyticsOn) { revokeAnalyticsConsent(); setAnalyticsOn(false); }
    else { grantAnalyticsConsent(); setAnalyticsOn(true); }
  };
  useDocumentMeta({
    title: 'Gizlilik & KVKK | Sinemood',
    description: "Sinemood'da hangi verilerin neden işlendiği, çerez/analitik kullanımı ve KVKK kapsamındaki haklarınız.",
  });

  const updated = '5 Eylül 2026';

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
      className="min-h-screen text-ivory font-sans">
      <header className="sticky top-0 z-40 backdrop-blur-md bg-[#120d0b]/70 border-b border-white/5 pt-safe">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <button onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-ivory/55 hover:text-ivory transition-colors group">
            <ChevronLeft size={18} className="group-hover:-translate-x-0.5 transition-transform" />
            <span className="text-[11px] font-bold uppercase tracking-widest">Geri</span>
          </button>
          <div className="flex items-center gap-2 text-amber">
            <ShieldCheck size={16} />
            <span className="text-[11px] font-bold uppercase tracking-[0.3em]">Gizlilik</span>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10 sm:py-14 pb-nav">
        <h1 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight mb-3">
          Gizlilik & KVKK Aydınlatma Metni
        </h1>
        <p className="text-fg-subtle text-sm mb-10">Son güncelleme: {updated}</p>

        <div className="space-y-8 text-[15px] leading-relaxed text-fg-muted">
          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">1. Veri Sorumlusu</h2>
            <p>
              Sinemood ("Platform"), ruh haline göre film keşfi sunan bir hizmettir. Bu metin,
              6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) kapsamında hangi verileri,
              hangi amaçla işlediğimizi açıklar.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">2. İşlenen Veriler</h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><span className="text-fg">Hesap bilgileri:</span> Google ile giriş yaptığınızda ad, e-posta ve profil görseliniz (yalnızca kimlik doğrulama ve profilinizi oluşturmak için).</li>
              <li><span className="text-fg">Uygulama içi veriler:</span> izleme listeniz, notlarınız, zevk haritanız, arkadaş/öneri etkileşimleriniz; hizmeti size sunmak için.</li>
              <li><span className="text-fg">Bildirim verileri:</span> bildirimlere izin verirseniz cihazınızın push adresi/jetonu (web push endpoint veya FCM token) ve seçtiğiniz bildirim saati. Bu jeton yalnız size bildirim ulaştırmak için kullanılır; reklam veya profilleme amacıyla kullanılmaz.</li>
              <li><span className="text-fg">Abonelik durumu:</span> Premium kullanıyorsanız yalnızca aboneliğin aktif olup olmadığı bilgisi. <span className="text-fg">Kart/ödeme bilgilerinizi görmez ve saklamayız</span> — ödeme tamamen Apple App Store veya Google Play üzerinden yürür.</li>
              <li><span className="text-fg">Anonim analitik:</span> sayfa görüntüleme ve özellik kullanımı (çerezsiz, IP saklanmaz, kişisel kimlik içermez). İstediğiniz zaman aşağıdan kapatabilirsiniz.</li>
              <li><span className="text-fg">Teknik veriler:</span> hata/performans amaçlı sınırlı günlükler.</li>
            </ul>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">2a. Bildirimler</h2>
            <p>
              Bildirimler <span className="text-fg">tamamen isteğe bağlıdır</span> ve yalnızca siz
              cihazınızda izin verdikten sonra gönderilir. İki tür bildirim vardır: size özel
              olanlar (arkadaşlık isteği, gelen film önerisi) ve günlük/haftalık içerik
              hatırlatmaları (günün filmi, haftalık rapor).
            </p>
            <p>
              Günlük bildirimin saatini Profil → Ayarlar → "Günlük Film Saati" bölümünden
              seçebilirsiniz. <span className="text-fg">Gece 00:00–08:00 arasında bildirim
              göndermeyiz.</span> Bildirimleri tamamen kapatmak için zil menüsündeki anahtarı
              kapatmanız veya cihaz ayarlarınızdan izni geri almanız yeterlidir; izni geri
              aldığınızda cihaz kaydınız silinir.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">3. İşleme Amaçları</h2>
            <p>
              Verileriniz; film önerisi sunmak, profil ve listelerinizi saklamak, sosyal özellikleri
              (arkadaş, öneri, davet) çalıştırmak ve hizmeti iyileştirmek için işlenir. Verileriniz
              üçüncü taraflara <span className="text-fg">satılmaz</span>.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">4. Çerezler & Analitik</h2>
            <p>
              Pazarlama/izleme çerezleri kullanmıyoruz. Analitik araçlarımız (Umami) <span className="text-fg">çerezsiz
              ve anonimdir</span>; çerez yerleştirmez, IP adresinizi saklamaz, kişisel kimlik toplamaz. Bu nedenle
              çerezsiz anonim ölçüm varsayılan olarak açıktır; dilediğiniz zaman aşağıdaki düğmeyle kapatabilirsiniz.
            </p>
            <div className="mt-3 flex items-center justify-between gap-4 rounded-2xl border border-default bg-fg/[0.03] px-4 py-3">
              <div>
                <p className="text-sm font-semibold text-fg">Anonim analitik</p>
                <p className="text-[12px] text-fg-subtle">{analyticsOn ? 'Şu an açık' : 'Şu an kapalı'}</p>
              </div>
              <button
                onClick={toggleAnalytics}
                aria-pressed={analyticsOn}
                className={`px-5 py-2.5 rounded-full text-[11px] font-bold uppercase tracking-[0.15em] transition-all ${
                  analyticsOn
                    ? 'border border-default text-fg-subtle hover:text-fg hover:bg-fg/[0.04]'
                    : 'bg-amber text-bg hover:scale-[1.02] active:scale-[0.99]'
                }`}
              >
                {analyticsOn ? 'Analitiği Kapat' : 'Analitiği Aç'}
              </button>
            </div>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">5. Herkese Açık İçerik & Topluluk Kuralları</h2>
            <p>
              "Söz" (film yorumu), topluluk önerileri ve herkese açık yaptığınız listeler{' '}
              <span className="text-fg">kullanıcı adınızla birlikte tüm kullanıcılara görünür</span>.
              Bu içerikleri dilediğiniz zaman silebilir veya gizleyebilirsiniz. Uygunsuz içerikleri
              her içeriğin yanındaki menüden <span className="text-fg">bildirebilir</span>, dilediğiniz
              kullanıcıyı <span className="text-fg">engelleyebilirsiniz</span> (içerikleri size görünmez
              olur). Bildirilen içerikler incelenir; kurallara aykırı olanlar kaldırılır.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">6. Üçüncü Taraf Servisler</h2>
            <p>
              Hizmeti sunabilmek için aşağıdaki sağlayıcılardan yararlanırız. Her birinin kendi
              gizlilik politikası geçerlidir:
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><span className="text-fg">TMDB &amp; OMDb</span> — film verileri, afiş ve künye bilgileri.</li>
              <li><span className="text-fg">Google</span> — hesabınızla giriş (Google ile Oturum Aç).</li>
              <li><span className="text-fg">Google Firebase (FCM) &amp; Apple (APNs)</span> — mobil uygulamada bildirim iletimi (cihaz jetonu).</li>
              <li><span className="text-fg">Anthropic &amp; Google Gemini</span> — film analizi ve öneri metinleri.</li>
              <li><span className="text-fg">RevenueCat, Apple App Store, Google Play</span> — Premium abonelik doğrulama ve ödeme (ödeme bilgisi bize ulaşmaz).</li>
              <li><span className="text-fg">Vercel, Railway, Turso</span> — site ve veritabanı barındırma.</li>
            </ul>
            <p>
              Film verileri TMDB tarafından sağlanır; Sinemood TMDB tarafından onaylanmamıştır.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">6a. Yurt Dışına Veri Aktarımı</h2>
            <p>
              Yukarıdaki barındırma ve servis sağlayıcılarının sunucuları Türkiye dışında (başta
              AB ve ABD) bulunabilir. Bu nedenle verileriniz KVKK md. 9 kapsamında
              <span className="text-fg"> yurt dışına aktarılmaktadır</span>. Aktarım, hizmetin
              teknik olarak sunulabilmesi için gereklidir ve sağlayıcılarla yapılan sözleşmeler ile
              standart koruma taahhütlerine dayanır. Bu aktarımı istemiyorsanız hizmeti
              kullanmamanız veya hesabınızı silmeniz gerekir.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">7. Saklama Süreleri & Güvenlik</h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><span className="text-fg">Hesap ve uygulama içi verileriniz:</span> hesabınız açık kaldığı sürece.</li>
              <li><span className="text-fg">Bildirim cihaz jetonu:</span> izni geri aldığınızda veya jeton geçersizleştiğinde silinir.</li>
              <li><span className="text-fg">Teknik günlükler:</span> en fazla 30 gün.</li>
              <li><span className="text-fg">Hesap silindiğinde:</span> tüm veriler derhal ve kalıcı olarak silinir.</li>
            </ul>
            <p>
              Profil → Ayarlar → "Hesabı Sil" ile hesabınızı sildiğinizde; izleme listeniz,
              notlarınız, Sözleriniz, listeleriniz, bildirim kayıtlarınız ve tüm sosyal
              verileriniz <span className="text-fg">kalıcı olarak silinir</span>. Verilere
              yetkisiz erişime karşı teknik tedbirler uygulanır (şifreli bağlantı, yetkilendirme
              kontrolleri, en az yetki ilkesi).
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">7a. Çocukların Verileri</h2>
            <p>
              Sinemood 13 yaş altındaki kullanıcılara yönelik değildir ve bilerek 13 yaş altından
              veri toplamayız. 13 yaş altında bir kullanıcıya ait veri işlendiğini fark edersek
              hesabı ve verileri sileriz. Böyle bir durumdan haberdarsanız bize bildirin.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">8. KVKK Haklarınız</h2>
            <p>
              KVKK md. 11 kapsamında; verilerinize erişme, düzeltme, silme ve işlemeye itiraz etme
              haklarına sahipsiniz. Bu hakları uygulama içinden doğrudan kullanabilirsiniz:
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><span className="text-fg">Erişim ve taşınabilirlik:</span> Profil → Ayarlar → "Verilerim" ile tüm verilerinizi JSON dosyası olarak indirin.</li>
              <li><span className="text-fg">Silme:</span> Profil → Ayarlar → "Hesabı Sil".</li>
              <li><span className="text-fg">Düzeltme:</span> profil bilgilerinizi Profil ekranından güncelleyin.</li>
              <li><span className="text-fg">İtiraz / kısıtlama:</span> analitiği bu sayfadan, bildirimleri zil menüsünden kapatın.</li>
            </ul>
            <p>
              Diğer talepleriniz için aşağıdaki adresten bize ulaşabilirsiniz; başvurular en geç
              30 gün içinde yanıtlanır.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">9. İletişim</h2>
            <p>
              Gizlilikle ilgili sorular için:{' '}
              <a href="mailto:privacy@sinemood.app" className="text-amber underline underline-offset-2 hover:text-amber/80">
                privacy@sinemood.app
              </a>
            </p>
            <p className="pt-1">
              Hizmet şartları ve topluluk kuralları için{' '}
              <button onClick={() => navigate('/kosullar')}
                className="text-amber underline underline-offset-2 hover:text-amber/80">
                Kullanım Koşulları
              </button>
              {' '}sayfasına bakabilirsiniz.
            </p>
          </section>
        </div>
      </main>
    </motion.div>
  );
}
