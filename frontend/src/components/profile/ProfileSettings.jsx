import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Settings, Bell, BellRing, Palette, Database, AlertTriangle, ChevronRight, ChevronDown, Clock, EyeOff, Ban, Crown,
  ShieldCheck, FileText,
} from 'lucide-react';
import {
  exportMyData, getNotifyTime, setNotifyTime, getNotifyPreferences, setNotifyPreference,
  setActivityVisibility, getBlockedUsers, unblockUser,
} from '../../services/api';
import { resolveAvatarUrl } from '../../utils/apiConfig';
import { getApiUrl } from '../../utils/apiConfig';
import { isPushSubscribed } from '../../utils/push';
import { isNative } from '../../utils/native';

/**
 * Günlük film bildirimi saati seçici — yalnız bu cihaz push'a aboneyse görünür.
 * Saat kullanıcının tüm cihazlarına uygulanır (backend per-user notify_hour).
 */
function NotifyTimeRow() {
  const [subscribed, setSubscribed] = useState(false);
  const [hour, setHour] = useState(18);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let alive = true;
    (async () => {
      const sub = await isPushSubscribed();
      if (!alive) return;
      setSubscribed(sub);
      if (sub) {
        try { const r = await getNotifyTime(); if (alive && r?.hour != null) setHour(r.hour); } catch { /* sessiz */ }
      }
    })();
    return () => { alive = false; };
  }, []);

  if (!subscribed) return null;

  const onChange = async (e) => {
    const h = parseInt(e.target.value, 10);
    setHour(h);
    try {
      const r = await setNotifyTime(h);
      if (r?.ok) { setSaved(true); setTimeout(() => setSaved(false), 1500); }
    } catch { /* sessiz */ }
  };

  return (
    <div className="w-full flex items-center gap-3.5 px-5 py-4">
      <Clock size={17} className="text-ivory/65" />
      <div className="flex-1 min-w-0">
        <p className="font-sans text-[14px] font-semibold text-ivory/80">Günlük Film Saati</p>
        <p className="font-sans text-[12px] text-ivory/60 mt-0.5">
          {saved ? 'Kaydedildi ✓' : 'Günün filmi bildiriminin saati'}
        </p>
      </div>
      <select
        value={hour}
        onChange={onChange}
        aria-label="Günlük bildirim saati"
        className="shrink-0 bg-amber/10 border border-amber/20 rounded-full px-3 py-1.5 font-sans text-[13px] font-bold text-amber/90 focus:outline-none focus:border-amber/50"
      >
        {Array.from({ length: 16 }, (_, i) => i + 8).map((h) => (
          <option key={h} value={h} className="bg-[#1c1512] text-ivory">
            {String(h).padStart(2, '0')}:00
          </option>
        ))}
      </select>
    </div>
  );
}

/**
 * Kategori bazlı bildirim tercihleri — yalnız bu cihaz push'a aboneyse görünür.
 * "Sosyal" kategorisi işlemseldir (biri sana bir şey gönderdi); diğerleri
 * içerik/pazarlama mesajlarıdır ve ayrı ayrı kapatılabilmeleri gerekir.
 */
const NOTIFY_CATEGORY_LABELS = [
  { key: 'social', label: 'Sosyal', desc: 'Arkadaşlık isteği, gelen film önerisi, davetler' },
  { key: 'daily', label: 'Günün Filmi', desc: 'Seçtiğin saatte günlük film önerisi' },
  { key: 'game', label: 'Oyun & Etkinlik', desc: 'Mood Kâhini yenilenmesi, ödül günleri' },
  { key: 'digest', label: 'Özet & Hatırlatma', desc: 'Haftalık rapor ve dönüş hatırlatmaları' },
];

function NotifyPrefsRow() {
  const [subscribed, setSubscribed] = useState(false);
  const [open, setOpen] = useState(false);
  const [prefs, setPrefs] = useState(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      const sub = await isPushSubscribed();
      if (!alive) return;
      setSubscribed(sub);
      if (!sub) return;
      try {
        const r = await getNotifyPreferences();
        if (alive && r?.preferences) setPrefs(r.preferences);
      } catch { /* sessiz */ }
    })();
    return () => { alive = false; };
  }, []);

  if (!subscribed) return null;

  const toggle = async (key) => {
    const next = !(prefs?.[key] ?? true);
    setPrefs((p) => ({ ...p, [key]: next }));
    const r = await setNotifyPreference(key, next);
    // Sunucu kaydedemediyse anahtarı geri al — kullanıcı kapattığını sanmasın.
    if (!r?.ok) setPrefs((p) => ({ ...p, [key]: !next }));
    else if (r.preferences) setPrefs(r.preferences);
  };

  const offCount = prefs
    ? NOTIFY_CATEGORY_LABELS.filter(({ key }) => prefs[key] === false).length
    : 0;

  return (
    <div>
      <button onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3.5 px-5 py-4 text-left transition-all hover:bg-white/[0.04]">
        <BellRing size={17} className="text-ivory/65" />
        <div className="flex-1 min-w-0">
          <p className="font-sans text-[14px] font-semibold text-ivory/80">Bildirim Türleri</p>
          <p className="font-sans text-[12px] text-ivory/60 mt-0.5">
            {offCount === 0 ? 'Hepsi açık' : `${offCount} tür kapalı`}
          </p>
        </div>
        {open ? <ChevronDown size={14} className="text-ivory/60 shrink-0" />
              : <ChevronRight size={14} className="text-ivory/60 shrink-0" />}
      </button>
      {open && (
        <div className="px-5 pb-4 space-y-2">
          {prefs === null ? (
            <p className="text-[12px] text-ivory/40">Yükleniyor...</p>
          ) : (
            NOTIFY_CATEGORY_LABELS.map(({ key, label, desc }) => {
              const on = prefs[key] !== false;
              return (
                <button key={key} onClick={() => toggle(key)}
                  role="switch" aria-checked={on} aria-label={label}
                  className="w-full flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/[0.05] text-left hover:border-white/[0.12] transition-all">
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] font-semibold text-ivory/80">{label}</p>
                    <p className="text-[11px] text-ivory/50 mt-0.5 leading-snug">{desc}</p>
                  </div>
                  <span className={`shrink-0 w-10 h-6 rounded-full p-0.5 transition-colors ${
                    on ? 'bg-amber/70' : 'bg-white/10'
                  }`}>
                    <span className={`block w-5 h-5 rounded-full bg-[#1c1512] transition-transform ${
                      on ? 'translate-x-4' : 'translate-x-0'
                    }`} />
                  </span>
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Settings shortcuts panel.
 */
function ActivityToggleRow() {
  const [hide, setHide] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let alive = true;
    const token = window.__fc_user_token;
    if (!token) return;
    (async () => {
      try {
        const res = await fetch(getApiUrl('/api/auth/me'), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const d = await res.json();
          if (alive) { setHide(!!d.hide_activity); setLoaded(true); }
        }
      } catch {}
    })();
    return () => { alive = false; };
  }, []);

  if (!loaded) return null;

  const toggle = async () => {
    const next = !hide;
    setHide(next);
    await setActivityVisibility(next);
  };

  return (
    <button onClick={toggle}
      className="w-full flex items-center gap-3.5 px-5 py-4 text-left transition-all hover:bg-white/[0.04]">
      <EyeOff size={17} className="text-ivory/65" />
      <div className="flex-1 min-w-0">
        <p className="font-sans text-[14px] font-semibold text-ivory/80">Aktivite Gizliliği</p>
        <p className="font-sans text-[12px] text-ivory/60 mt-0.5">
          {hide ? 'Aktiviten arkadaşlarından gizli' : 'Aktiviten arkadaşlarına görünür'}
        </p>
      </div>
      <span className={`px-2.5 py-1 rounded-full border font-sans text-[11px] font-bold uppercase tracking-wide shrink-0 ${
        hide ? 'bg-rose-500/10 border-rose-500/20 text-rose-400/70' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400/70'
      }`}>
        {hide ? 'Gizli' : 'Açık'}
      </span>
      <ChevronRight size={14} className="text-ivory/60 shrink-0" />
    </button>
  );
}

/** Engellenen kullanıcılar yönetimi — UGC moderasyonunun kullanıcı tarafı. */
function BlockedUsersRow() {
  const [open, setOpen] = useState(false);
  const [blocked, setBlocked] = useState(null);

  const load = async () => {
    const d = await getBlockedUsers();
    setBlocked(d.blocked || []);
  };

  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (next && blocked === null) load();
  };

  const handleUnblock = async (id) => {
    try { await unblockUser(id); } catch { /* sessiz */ }
    setBlocked((b) => (b || []).filter((u) => u.id !== id));
  };

  return (
    <div>
      <button onClick={toggle}
        className="w-full flex items-center gap-3.5 px-5 py-4 text-left transition-all hover:bg-white/[0.04]">
        <Ban size={17} className="text-ivory/65" />
        <div className="flex-1 min-w-0">
          <p className="font-sans text-[14px] font-semibold text-ivory/80">Engellenen Kullanıcılar</p>
          <p className="font-sans text-[12px] text-ivory/60 mt-0.5">İçerikleri sana görünmez</p>
        </div>
        {open ? <ChevronDown size={14} className="text-ivory/60 shrink-0" />
              : <ChevronRight size={14} className="text-ivory/60 shrink-0" />}
      </button>
      {open && (
        <div className="px-5 pb-4 space-y-2">
          {blocked === null ? (
            <p className="text-[12px] text-ivory/40">Yükleniyor...</p>
          ) : blocked.length === 0 ? (
            <p className="text-[12px] text-ivory/40 italic">Engellediğin kimse yok.</p>
          ) : (
            blocked.map((u) => (
              <div key={u.id} className="flex items-center gap-2.5 p-2 rounded-xl bg-white/[0.03] border border-white/[0.05]">
                <span className="w-7 h-7 rounded-full overflow-hidden bg-white/10 shrink-0">
                  {u.avatar
                    ? <img src={resolveAvatarUrl(u.avatar)} alt="" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                    : <span className="w-full h-full flex items-center justify-center text-[11px] font-bold text-amber/60">{(u.username || '?')[0].toUpperCase()}</span>}
                </span>
                <p className="flex-1 text-[12px] font-semibold text-ivory/80 truncate">@{u.username}</p>
                <button onClick={() => handleUnblock(u.id)}
                  className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold uppercase tracking-wider text-ivory/60 hover:text-ivory hover:border-white/25 transition-all">
                  Engeli Kaldır
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default function ProfileSettings({ theme, toggleTheme, logout, navigate, onNotifOpen, onPremiumOpen }) {
  const settings = [
    ...(isNative ? [{
      icon: Crown, label: 'Premium', desc: 'Film deneyimini yükselt',
      action: onPremiumOpen, badge: 'Yükselt', premium: true,
    }] : []),
    {
      icon: Bell, label: 'Bildirimler', desc: 'Öneri ve istek bildirimleri',
      action: onNotifOpen,
    },
    {
      icon: Palette, label: 'Görünüm',
      desc: theme === 'dark' ? 'Aydınlık temaya geç' : 'Karanlık temaya geç',
      action: toggleTheme,
      badge: theme === 'dark' ? 'Karanlık' : 'Aydınlık',
    },
    {
      icon: Database, label: 'Verilerim', desc: 'Tüm verilerini indir (KVKK md. 11)',
      action: async () => {
        try {
          // Yalnız izleme listesi indiriliyordu; gizlilik metni ise tüm
          // verilere erişim hakkı vaat ediyor. Sunucu artık hepsini döndürür.
          const data = await exportMyData();
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url; a.download = 'sinemood-verilerim.json'; a.click();
          URL.revokeObjectURL(url);
        } catch { alert('Veri dışa aktarılamadı. Lütfen tekrar deneyin.'); }
      },
    },
    {
      icon: ShieldCheck, label: 'Gizlilik & KVKK', desc: 'Hangi veriler, neden işleniyor',
      action: () => navigate('/gizlilik'),
    },
    {
      icon: FileText, label: 'Kullanım Koşulları', desc: 'Hizmet şartları ve topluluk kuralları',
      action: () => navigate('/kosullar'),
    },
    {
      icon: AlertTriangle, label: 'Hesabı Sil', desc: 'Tüm verileri kalıcı olarak sil', danger: true,
      action: async () => {
        if (!window.confirm('Hesabınız ve tüm verileriniz kalıcı olarak silinecek. Bu işlem geri alınamaz. Emin misiniz?')) return;
        try {
          const token = window.__fc_user_token;
          const res = await fetch(getApiUrl('/api/auth/account'), {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (res.ok) { logout(); navigate('/'); }
          else alert('Hesap silinemedi. Lütfen tekrar deneyin.');
        } catch { alert('Bir hata oluştu.'); }
      },
    },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.40, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-3">

      <div className="flex items-center gap-2.5 px-1">
        <Settings size={14} className="text-amber/50" />
        <p className="font-sans text-[11px] font-bold uppercase tracking-[0.25em] text-amber/50">
          Ayarlar
        </p>
      </div>

      <div className="rounded-2xl bg-[#1c1512]/90 border border-white/[0.06] overflow-hidden divide-y divide-white/[0.04]">
        <NotifyTimeRow />
        <NotifyPrefsRow />
        <ActivityToggleRow />
        <BlockedUsersRow />
        {settings.map(({ icon: Icon, label, desc, danger, action, badge, premium }) => (
          <button key={label} onClick={action}
            className={`w-full flex items-center gap-3.5 px-5 py-4 text-left transition-all
              ${danger ? 'hover:bg-rose-500/8' : 'hover:bg-white/[0.04]'}`}>
            <Icon size={17} className={premium ? 'text-amber-400' : danger ? 'text-rose-400/70' : 'text-ivory/65'} />
            <div className="flex-1 min-w-0">
              <p className={`font-sans text-[14px] font-semibold ${danger ? 'text-rose-400/80' : 'text-ivory/80'}`}>
                {label}
              </p>
              <p className="font-sans text-[12px] text-ivory/60 mt-0.5">{desc}</p>
            </div>
            {badge && (
              <span className="px-2.5 py-1 rounded-full bg-amber/10 border border-amber/20 font-sans text-[11px] font-bold text-amber/70 uppercase tracking-wide shrink-0">
                {badge}
              </span>
            )}
            <ChevronRight size={14} className="text-ivory/60 shrink-0" />
          </button>
        ))}
      </div>
    </motion.div>
  );
}
