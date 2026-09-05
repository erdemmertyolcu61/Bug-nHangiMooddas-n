import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ScrollText } from 'lucide-react';
import { motion } from 'framer-motion';
import useDocumentMeta from '../utils/useDocumentMeta';

/**
 * Kullanım Koşulları (EULA).
 * App Store Guideline 1.2 (kullanıcı üretimi içerik) ve 3.1.2 (otomatik
 * yenilenen abonelik) ile Google Play, mağazada listelenebilmek için bu metni
 * ve uygulama içinden erişilebilir bir bağlantıyı şart koşar.
 */
export default function Kosullar() {
  const navigate = useNavigate();
  useDocumentMeta({
    title: 'Kullanım Koşulları | Sinemood',
    description: "Sinemood hizmet şartları, topluluk kuralları, abonelik ve cayma hakkı koşulları.",
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
            <ScrollText size={16} />
            <span className="text-[11px] font-bold uppercase tracking-[0.3em]">Koşullar</span>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10 sm:py-14 pb-nav">
        <h1 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight mb-3">
          Kullanım Koşulları
        </h1>
        <p className="text-fg-subtle text-sm mb-10">Son güncelleme: {updated}</p>

        <div className="space-y-8 text-[15px] leading-relaxed text-fg-muted">
          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">1. Kapsam</h2>
            <p>
              Bu koşullar, Sinemood ("Platform") web sitesi ve mobil uygulamalarını kullanımınızı
              düzenler. Platformu kullanarak bu koşulları kabul etmiş olursunuz. Kabul etmiyorsanız
              lütfen Platformu kullanmayın.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">2. Hizmet</h2>
            <p>
              Sinemood, ruh halinize göre film önerileri sunan; izleme listesi, not, liste,
              yorum ("Söz") ve arkadaş özellikleri içeren bir keşif hizmetidir. Öneriler
              <span className="text-fg"> bilgilendirme amaçlıdır</span>; film içerikleri, yaş
              sınırları ve erişilebilirlik üçüncü taraf kaynaklardan gelir ve garanti edilmez.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">3. Hesap ve Yaş Sınırı</h2>
            <p>
              Hesap açmak için <span className="text-fg">en az 13 yaşında</span> olmalısınız.
              13–18 yaş arasındaysanız Platformu veli/vasi onayıyla kullanabilirsiniz. Hesap
              güvenliğinizden ve hesabınız üzerinden yapılan işlemlerden siz sorumlusunuz.
              Hesabınızı ve tüm verilerinizi istediğiniz an Profil → Ayarlar → "Hesabı Sil"
              ile kalıcı olarak silebilirsiniz.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">4. Kullanıcı İçeriği ve Topluluk Kuralları</h2>
            <p>
              Paylaştığınız Sözler, listeler ve profil bilgileri size aittir; bunları Platformda
              göstermemiz için bize sınırlı bir kullanım izni vermiş olursunuz. İçeriğinizi
              dilediğiniz zaman silebilirsiniz.
            </p>
            <p className="pt-1">Platformda <span className="text-fg">kesinlikle yasaktır</span>:</p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Hakaret, nefret söylemi, taciz, tehdit veya zorbalık</li>
              <li>Cinsel içerik, şiddet özendirme, yasa dışı faaliyet çağrısı</li>
              <li>Başkasının kimliğine bürünme, spam, reklam, dolandırıcılık</li>
              <li>Telif hakkı ihlali; korsan yayın/indirme bağlantısı paylaşımı</li>
              <li>Otomatik araçlarla toplu veri çekme veya sistemi kötüye kullanma</li>
            </ul>
            <p className="pt-1">
              <span className="text-fg">Sıfır tolerans:</span> Her içeriğin yanındaki menüden
              uygunsuz içeriği bildirebilir, dilediğiniz kullanıcıyı engelleyebilirsiniz.
              Bildirilen içerikler <span className="text-fg">24 saat içinde</span> incelenir;
              kurallara aykırı olanlar kaldırılır ve ilgili hesap askıya alınabilir veya
              kapatılabilir.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">5. Premium Abonelik</h2>
            <p>
              Premium, <span className="text-fg">otomatik yenilenen</span> bir aboneliktir.
              Ücretlendirme ve yenileme, uygulamayı indirdiğiniz mağaza hesabınız (Apple App Store
              veya Google Play) üzerinden yapılır; ödeme bilgilerinizi Sinemood görmez ve saklamaz.
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Abonelik, dönem bitiminden en az 24 saat önce iptal edilmezse otomatik yenilenir.</li>
              <li>İptal: cihazınızın mağaza hesabı ayarlarından yapılır (Apple: Ayarlar → Apple Kimliği → Abonelikler; Google: Play Store → Abonelikler).</li>
              <li>Ücret iadesi talepleri ilgili mağazanın iade politikasına tabidir.</li>
              <li>Güncel fiyat ve dönem, satın alma ekranında satın almadan önce gösterilir.</li>
            </ul>
            <p className="pt-1">
              <span className="text-fg">Cayma hakkı:</span> 6502 sayılı Tüketicinin Korunması
              Hakkında Kanun uyarınca dijital içerik ve hizmetlerde, hizmet ifasına tüketicinin
              onayıyla derhal başlanması hâlinde cayma hakkı kullanılamaz. Satın alma anında bu
              onayı vermiş sayılırsınız.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">6. Fikri Mülkiyet</h2>
            <p>
              Platformun tasarımı, metinleri ve yazılımı Sinemood'a aittir. Film verileri, afişler
              ve fragmanlar TMDB, OMDb ve YouTube gibi üçüncü taraflara aittir ve onların kullanım
              şartlarına tabidir. <span className="text-fg">Sinemood TMDB tarafından onaylanmamış
              veya sertifikalandırılmamıştır.</span>
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">7. Sorumluluğun Sınırı</h2>
            <p>
              Platform "olduğu gibi" sunulur. Kesintisiz veya hatasız çalışacağı garanti edilmez.
              Üçüncü taraf servislerden (film verisi, yayın platformları, kimlik doğrulama)
              kaynaklanan kesinti ve hatalardan sorumlu değiliz. Zorunlu yasal sorumluluklarımız
              saklıdır; bu madde tüketici mevzuatından doğan haklarınızı sınırlamaz.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">8. Askıya Alma ve Fesih</h2>
            <p>
              Bu koşulların ihlali hâlinde hesabınızı uyarı yaparak veya ağır ihlallerde derhal
              askıya alabilir ya da kapatabiliriz. Siz de dilediğiniz zaman hesabınızı silerek
              sözleşmeyi sonlandırabilirsiniz.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">9. Değişiklikler</h2>
            <p>
              Bu koşulları güncelleyebiliriz. Önemli değişikliklerde uygulama içinde bilgilendirme
              yaparız. Değişiklik sonrası kullanıma devam etmeniz güncel koşulları kabul ettiğiniz
              anlamına gelir.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">10. Uygulanacak Hukuk ve Uyuşmazlık</h2>
            <p>
              Bu koşullara Türkiye Cumhuriyeti hukuku uygulanır. Tüketici sıfatıyla, parasal
              sınırlara göre Tüketici Hakem Heyetlerine veya Tüketici Mahkemelerine
              başvurabilirsiniz.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-lg font-bold text-fg">11. İletişim</h2>
            <p>
              Sorularınız ve içerik bildirimleriniz için:{' '}
              <a href="mailto:destek@sinemood.app" className="text-amber underline underline-offset-2 hover:text-amber/80">
                destek@sinemood.app
              </a>
              . Gizlilikle ilgili talepler için{' '}
              <button onClick={() => navigate('/gizlilik')}
                className="text-amber underline underline-offset-2 hover:text-amber/80">
                Gizlilik &amp; KVKK Aydınlatma Metni
              </button>
              .
            </p>
          </section>
        </div>
      </main>
    </motion.div>
  );
}
