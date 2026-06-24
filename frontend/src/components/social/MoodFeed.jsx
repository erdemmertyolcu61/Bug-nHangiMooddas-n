import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Eye, Bookmark, Send, ChevronLeft, Film, Users, Heart, MessageCircle, Loader2, RefreshCw, Compass } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getSocialFeed, likeActivity, unlikeActivity, commentOnActivity, reactToMood } from '../../services/api';
import { resolveAvatarUrl } from '../../utils/apiConfig';
import { proxyImageUrl } from '../../services/api';
import { MOODS } from '../../context/MoodContext';
import { useAuth } from '../../context/AuthContext';
import RecommendMovieSheet from '../RecommendMovieSheet';
import FilmDetailModal from '../FilmDetailModal';
import DailyFilmBanner from '../DailyFilmBanner';
import TrendingStrip from './TrendingStrip';
import PeopleDiscovery from './PeopleDiscovery';
import DailyChallenge from './DailyChallenge';
import useDocumentMeta from '../../utils/useDocumentMeta';

function timeAgo(dateStr) {
  if (!dateStr) return '';
  let s = String(dateStr).replace(' ', 'T');
  if (!s.endsWith('Z') && !s.includes('+')) s += 'Z';
  const d = new Date(s);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return 'Az once';
  if (diff < 3600) return `${Math.floor(diff / 60)}dk`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}sa`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}g`;
  return new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'short' }).format(d);
}

// ─── Mood Kartı (Emoji Reaksiyon destekli) ─────────────────────────────
function MoodCard({ fm, onRecommend, onReact }) {
  const mood = MOODS[fm.mood_id];
  const MoodIcon = mood?.icon;
  const color = mood?.accentHex || '#d4af37';
  const [showReactions, setShowReactions] = useState(false);
  const [sentEmoji, setSentEmoji] = useState(null);
  const REACTION_EMOJIS = ['🔥', '🫂', '😂', '🎬'];

  const handleReact = async (emoji) => {
    setSentEmoji(emoji);
    setShowReactions(false);
    onReact?.(fm.user_id, emoji);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
      className="shrink-0 w-[104px] sm:w-[124px] p-2.5 sm:p-3.5 rounded-2xl bg-[#1a1310] border border-white/[0.06] space-y-2 sm:space-y-2.5 relative"
    >
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full overflow-hidden bg-white/10 shrink-0">
          {fm.avatar ? (
            <img src={resolveAvatarUrl(fm.avatar)} alt="" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-amber/60 font-bold text-sm">
              {(fm.username || '?')[0].toUpperCase()}
            </div>
          )}
        </div>
        <p className="text-[11px] sm:text-[12px] font-semibold text-ivory truncate">@{fm.username}</p>
      </div>
      <div className="flex items-center gap-1.5 sm:gap-2">
        {MoodIcon && <MoodIcon size={15} className="sm:size-[16px]" style={{ color }} />}
        <span className="text-[12px] sm:text-[13px] font-serif font-bold" style={{ color }}>
          {mood?.title || fm.mood_id}
        </span>
      </div>

      <p className="text-[10px] sm:text-[11px] text-white/30">{timeAgo(fm.updated_at)}</p>

      {/* Aksiyon butonları */}
      <div className="flex gap-1.5 mt-1">
        <button
          onClick={() => onRecommend({ id: fm.user_id, name: fm.name, username: fm.username, avatar: fm.avatar })}
          className="w-full flex items-center justify-center gap-1 py-1.5 sm:py-2 rounded-xl text-[10px] sm:text-[10px] font-bold uppercase tracking-wider
            bg-amber/12 border border-amber/20 text-amber hover:bg-amber/20 transition-all"
        >
          <Send size={9} className="sm:size-[10px]" /> Öner
        </button>
      </div>
    </motion.div>
  );
}

// ─── Aktivite Kartı (Beğeni + Yorum destekli, Ambient Glow) ───────────
function ActivityCard({ a, i, onFilmClick }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
      transition={{ delay: i * 0.03 }}
      className="relative rounded-xl bg-[#1a1310] border border-white/[0.06] hover:border-amber/20 transition-all overflow-hidden"
    >
      {/* Ambient Glow (poster renginden hafif ışıma) */}
      {a.poster_url && (
        <div className="absolute -right-4 -top-4 w-24 h-24 opacity-[0.08] blur-2xl pointer-events-none">
          <img src={proxyImageUrl(a.poster_url)} alt="" className="w-full h-full object-cover rounded-full" />
        </div>
      )}

      {/* Ana içerik */}
      <button
        onClick={() => onFilmClick({ id: a.tmdb_id, title: a.title, poster_url: a.poster_url })}
        className="w-full flex items-center gap-3 p-3 text-left relative z-[1]"
      >
        <div className="w-9 h-9 rounded-full overflow-hidden bg-white/10 shrink-0">
          {a.avatar ? (
            <img src={resolveAvatarUrl(a.avatar)} alt="" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-amber/60 font-bold text-xs">
              {(a.username || '?')[0].toUpperCase()}
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[12px] text-ivory/80 truncate">
            <span className="font-semibold text-amber/70">@{a.username}</span>{' '}
            {a.action_type === 'watched' ? 'izledi' : 'kaydetti'}
          </p>
          <p className="text-[13px] font-serif font-semibold text-ivory truncate">{a.title}</p>
        </div>
        {a.poster_url && (
          <img src={proxyImageUrl(a.poster_url)} alt=""
            className="w-10 h-[60px] rounded-lg object-cover bg-white/5 shrink-0 shadow-[0_0_12px_rgba(212,175,55,0.08)]" loading="lazy" />
        )}
      </button>

      {/* Zaman Barı */}
      <div className="flex justify-end px-3 pb-2.5 pt-0 relative z-[1]">
        <div className="flex items-center gap-1.5">
          {a.action_type === 'watched'
            ? <Eye size={12} className="text-emerald-400/40" />
            : <Bookmark size={12} className="text-amber/30" />}
          <span className="text-[9px] text-white/20">{timeAgo(a.action_at)}</span>
        </div>
      </div>

    </motion.div>
  );
}

// ─── Ana MoodFeed Bileşeni ─────────────────────────────────────────────
export default function MoodFeed() {
  useDocumentMeta({ title: 'Akis | Sinemood', description: 'Arkadaslarinin mood ve film aktivitesi.' });
  const navigate = useNavigate();
  const { user } = useAuth();
  const [feed, setFeed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recommendTarget, setRecommendTarget] = useState(null);
  const [filmDetail, setFilmDetail] = useState(null);

  const [feedError, setFeedError] = useState(false);

  // Pagination state
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const loadMoreRef = useRef(null);

  // Pull-to-refresh state
  const [refreshing, setRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const touchStartY = useRef(0);
  const scrollContainerRef = useRef(null);
  const isPulling = useRef(false);

  // Veriyi çek (ilk yükleme veya yenileme)
  const fetchFeed = useCallback(async (pageNum = 1, append = false) => {
    try {
      setFeedError(false);
      const data = await getSocialFeed(pageNum);
      if (append && feed) {
        setFeed(prev => ({
          ...prev,
          activities: [...(prev?.activities || []), ...(data.activities || [])],
          has_more: data.has_more,
        }));
      } else {
        setFeed(data);
      }
      setHasMore(data.has_more || false);
      setPage(pageNum);
    } catch {
      setFeedError(true);
      if (!append) setFeed({ friend_moods: [], activities: [], recommendations: [], has_more: false });
    }
  }, [feed]);

  // İlk yükleme
  useEffect(() => {
    if (!user) { setLoading(false); return; }
    let alive = true;
    (async () => {
      await fetchFeed(1);
      if (alive) setLoading(false);
    })();
    return () => { alive = false; };
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  // ─── Pull-to-Refresh (Touch Events) ──────────────────────────
  const PULL_THRESHOLD = 80;

  const onTouchStart = useCallback((e) => {
    const container = scrollContainerRef.current;
    if (!container || container.scrollTop > 10) return;
    touchStartY.current = e.touches[0].clientY;
    isPulling.current = true;
  }, []);

  const onTouchMove = useCallback((e) => {
    if (!isPulling.current || refreshing) return;
    const dy = e.touches[0].clientY - touchStartY.current;
    if (dy > 0) {
      setPullDistance(Math.min(dy * 0.5, 120)); // dampening
    }
  }, [refreshing]);

  const onTouchEnd = useCallback(async () => {
    if (!isPulling.current) return;
    isPulling.current = false;
    if (pullDistance >= PULL_THRESHOLD && !refreshing) {
      setRefreshing(true);
      setPullDistance(PULL_THRESHOLD);
      await fetchFeed(1);
      setRefreshing(false);
    }
    setPullDistance(0);
  }, [pullDistance, refreshing, fetchFeed]);

  // ─── Infinite Scroll (IntersectionObserver) ──────────────────
  useEffect(() => {
    const el = loadMoreRef.current;
    if (!el || !hasMore) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && hasMore && !loadingMore) {
          setLoadingMore(true);
          fetchFeed(page + 1, true).finally(() => setLoadingMore(false));
        }
      },
      { threshold: 0.1 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [hasMore, loadingMore, page, fetchFeed]);

  // ─── Mood Reaksiyonu ─────────────────────────────────────────
  const handleMoodReact = async (targetUserId, emoji) => {
    await reactToMood(targetUserId, emoji);
  };

  // Login'siz: trend + günün filmi yine görünür (boş ekran yok), giriş CTA'sı altta
  if (!user) {
    return (
      <div className="min-h-screen pb-28 pt-6 px-2 sm:px-6 max-w-2xl mx-auto space-y-8">
        <div className="px-1">
          <p className="text-[9px] sm:text-[10px] font-bold uppercase tracking-[0.4em] sm:tracking-[0.6em] text-amber/60">SOSYAL</p>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold tracking-tight">Akış</h1>
        </div>
        <TrendingStrip />
        <DailyChallenge />
        <DailyFilmBanner />
        <PeopleDiscovery loggedIn={false} />
        <div className="flex flex-col items-center justify-center py-14 text-center rounded-2xl bg-[#1a1310] border border-white/[0.06]">
          <div className="w-16 h-16 rounded-full bg-amber/10 border border-amber/20 flex items-center justify-center mb-4">
            <Compass size={28} className="text-amber/50" />
          </div>
          <p className="font-serif text-lg text-ivory/60 mb-1">Akışın henüz sessiz</p>
          <p className="text-[12px] text-white/30 max-w-[240px] mb-5 leading-relaxed">
            Arkadaşlarının aktivitesini görmek ve sinema dünyasına katılmak için giriş yap!
          </p>
          <button onClick={() => navigate('/profil')}
            className="px-6 py-2.5 rounded-full bg-amber/15 text-amber border border-amber/30 text-xs font-bold uppercase tracking-wider hover:bg-amber/25 transition-all">
            <span className="flex items-center gap-2">
              <Users size={14} /> Giriş Yap
            </span>
          </button>
        </div>
      </div>
    );
  }

  const hasFeedContent = feed?.friend_moods?.length > 0 || feed?.activities?.length > 0 || feed?.recommendations?.length > 0;

  return (
    <>
      <header className="sticky top-0 z-50 bg-[#120d0b]/98 border-b border-white/5 pt-safe">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6 flex items-center justify-between">
          <div className="flex items-center gap-3 sm:gap-6">
            <button onClick={() => navigate(-1)}
              className="p-3 -ml-1 hover:bg-white/5 rounded-full transition-all tap-target flex items-center justify-center">
              <ChevronLeft size={24} />
            </button>
            <div>
              <p className="text-[9px] sm:text-[10px] font-bold uppercase tracking-[0.4em] sm:tracking-[0.6em] text-amber/60">SOSYAL</p>
              <h1 className="font-serif text-2xl sm:text-3xl font-bold tracking-tight">Akış</h1>
            </div>
          </div>
        </div>
      </header>

    <div
      ref={scrollContainerRef}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      {/* Pull-to-Refresh İndikatörü */}
      <AnimatePresence>
        {pullDistance > 10 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center py-3"
            style={{ height: pullDistance }}
          >
            <motion.div
              animate={refreshing ? { rotate: 360 } : { rotate: pullDistance * 2 }}
              transition={refreshing ? { repeat: Infinity, duration: 0.8, ease: 'linear' } : { duration: 0 }}
            >
              <RefreshCw
                size={22}
                className={`transition-colors ${pullDistance >= PULL_THRESHOLD ? 'text-amber' : 'text-white/30'}`}
              />
            </motion.div>
            {pullDistance >= PULL_THRESHOLD && !refreshing && (
              <span className="ml-2 text-[11px] text-amber/60 font-medium">Bırak & Yenile</span>
            )}
            {refreshing && (
              <span className="ml-2 text-[11px] text-amber/60 font-medium">Yenileniyor...</span>
            )}
          </motion.div>
        )}
      </AnimatePresence>

    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }}
      className="min-h-screen pb-28 pt-4 sm:pt-6 px-2 sm:px-6 max-w-2xl mx-auto"
    >

      {loading ? (
        <div className="space-y-6 py-4">
          <div className="animate-pulse">
            <div className="h-4 bg-white/8 rounded w-1/3 mb-4" />
            <div className="flex gap-3 overflow-hidden">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="w-20 shrink-0 space-y-2">
                  <div className="w-14 h-14 mx-auto rounded-full bg-white/8" />
                  <div className="h-2.5 bg-white/6 rounded w-full" />
                </div>
              ))}
            </div>
          </div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse flex gap-3 p-4 rounded-2xl bg-white/[0.02] border border-white/5">
              <div className="w-10 h-10 rounded-full bg-white/8 shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="h-3.5 bg-white/8 rounded w-2/5" />
                <div className="h-3 bg-white/6 rounded w-4/5" />
              </div>
              <div className="w-10 h-[60px] rounded-lg bg-white/5 shrink-0" />
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-6 sm:space-y-8">
          {/* Bu Hafta Toplulukta — topluluk trendi, her zaman dolu (soguk baslangic) */}
          <TrendingStrip />

          {/* Haftanin Sorusu */}
          <DailyChallenge />

          {/* Gunun Filmi — her zaman goster (feed bos olsa bile) */}
          <DailyFilmBanner />

          {/* Section 1: Arkadaslarin Moodlari */}
          {feed?.friend_moods?.length > 0 && (
            <section>
              <SectionHeader text="Arkadaşların Mood'u" />
              <div className="flex gap-2.5 sm:gap-3 overflow-x-auto pb-2 no-scrollbar -mx-2 sm:-mx-4 px-2 sm:px-4">
                {feed.friend_moods.map((fm) => (
                  <MoodCard
                    key={fm.user_id}
                    fm={fm}
                    onRecommend={setRecommendTarget}
                    onReact={handleMoodReact}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Section 2: Arkadas Aktivitesi */}
          {feed?.activities?.length > 0 && (
            <section>
              <SectionHeader text="Arkadaş Aktivitesi" />
              <div className="space-y-2">
                {feed.activities.map((a, i) => (
                  <ActivityCard
                    key={`${a.user_id}-${a.tmdb_id}-${i}`}
                    a={a}
                    i={i}
                    onFilmClick={setFilmDetail}
                    onLike={() => {}}
                    onComment={() => {
                      // Yorum sayısını optimistik artır
                      setFeed(prev => {
                        if (!prev) return prev;
                        const newActivities = [...prev.activities];
                        const idx = newActivities.findIndex(
                          act => act.user_id === a.user_id && act.tmdb_id === a.tmdb_id && act.action_type === a.action_type
                        );
                        if (idx !== -1) {
                          newActivities[idx] = { ...newActivities[idx], comment_count: (newActivities[idx].comment_count || 0) + 1 };
                        }
                        return { ...prev, activities: newActivities };
                      });
                    }}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Section 3: Son Oneriler */}
          {feed?.recommendations?.length > 0 && (
            <section>
              <SectionHeader text="Son Gelen Öneriler" />
              <div className="space-y-2">
                {feed.recommendations.map((r) => (
                  <motion.button key={r.id}
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                    onClick={() => setFilmDetail({ id: r.movie_id, title: r.movie_title, poster_url: r.poster_url })}
                    className="w-full flex items-center gap-3 p-3 rounded-xl bg-[#1a1310] border border-white/[0.06] hover:border-amber/20 transition-all text-left relative overflow-hidden"
                  >
                    {/* Ambient Glow */}
                    {r.poster_url && (
                      <div className="absolute -left-4 -top-4 w-20 h-20 opacity-[0.07] blur-2xl pointer-events-none">
                        <img src={proxyImageUrl(r.poster_url)} alt="" className="w-full h-full object-cover rounded-full" />
                      </div>
                    )}
                    {r.poster_url ? (
                      <img src={proxyImageUrl(r.poster_url)} alt=""
                        className="w-10 h-[60px] rounded-lg object-cover bg-white/5 shrink-0 shadow-[0_0_12px_rgba(212,175,55,0.08)] relative z-[1]" loading="lazy" />
                    ) : (
                      <div className="w-10 h-[60px] rounded-lg bg-white/5 flex items-center justify-center shrink-0 relative z-[1]">
                        <Film size={14} className="text-white/20" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0 relative z-[1]">
                      <p className="text-[11px] text-white/40">
                        <span className="text-amber/70 font-semibold">@{r.sender?.username || 'arkadas'}</span> önerdi
                      </p>
                      <p className="text-[13px] font-serif font-semibold text-ivory truncate">{r.movie_title}</p>
                      {r.user_note && (
                        <p className="text-[11px] font-serif italic text-white/40 truncate">{r.user_note}</p>
                      )}
                    </div>
                    <span className="text-[9px] text-white/25 shrink-0 relative z-[1]">{timeAgo(r.created_at)}</span>
                  </motion.button>
                ))}
              </div>
            </section>
          )}

          {/* Kisi kesfi — arkadas aktivitesi azsa one cikar */}
          {!hasFeedContent && <PeopleDiscovery loggedIn />}

          {/* Geliştirilmiş Empty State */}
          {!hasFeedContent && (
            <div className="flex flex-col items-center justify-center py-14 text-center rounded-2xl bg-[#1a1310] border border-white/[0.06]">
              {feedError ? (
                <>
                  <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-4">
                    <Activity size={28} className="text-rose-400" />
                  </div>
                  <p className="font-serif text-lg text-ivory/60 mb-1">Bağlantı Sorunu</p>
                  <p className="text-[12px] text-white/30 max-w-[240px] mb-5 leading-relaxed">
                    Sunucuya ulaşılamadı veya uyanıyor olabilir. Lütfen tekrar dene.
                  </p>
                  <button
                    onClick={() => { setLoading(true); fetchFeed(1).finally(() => setLoading(false)); }}
                    className="px-6 py-2.5 rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 text-xs font-bold uppercase tracking-wider hover:bg-rose-500/25 transition-all"
                  >
                    <span className="flex items-center gap-2">
                      <RefreshCw size={14} /> Tekrar Dene
                    </span>
                  </button>
                </>
              ) : (
                <>
                  <div className="w-16 h-16 rounded-full bg-amber/10 border border-amber/20 flex items-center justify-center mb-4">
                    <Compass size={28} className="text-amber/50" />
                  </div>
                  <p className="font-serif text-lg text-ivory/60 mb-1">Akışın henüz sessiz</p>
                  <p className="text-[12px] text-white/30 max-w-[240px] mb-5 leading-relaxed">
                    Film gurularını keşfet, arkadaş ekle ve birlikte sinema dünyasını keşfedin!
                  </p>
                  <button
                    onClick={() => navigate('/profil?tab=social')}
                    className="px-6 py-2.5 rounded-full bg-amber/15 text-amber border border-amber/30 text-xs font-bold uppercase tracking-wider hover:bg-amber/25 transition-all"
                  >
                    <span className="flex items-center gap-2">
                      <Users size={14} /> Film Gurularını Keşfet
                    </span>
                  </button>
                </>
              )}
            </div>
          )}

          {/* Infinite Scroll Sentinel */}
          {hasMore && (
            <div ref={loadMoreRef} className="flex items-center justify-center py-6">
              {loadingMore ? (
                <div className="flex items-center gap-2 text-white/30">
                  <Loader2 size={16} className="animate-spin" />
                  <span className="text-[11px] font-medium">Daha fazla yükleniyor...</span>
                </div>
              ) : (
                <div className="h-4" /> // invisible sentinel
              )}
            </div>
          )}

          {/* Son sayfa mesajı */}
          {!hasMore && feed?.activities?.length > 0 && page > 1 && (
            <p className="text-center text-[11px] text-white/15 py-4 font-medium">
              Tüm aktiviteler gösterildi ✨
            </p>
          )}
        </div>
      )}

      {recommendTarget && (
        <RecommendMovieSheet targetUser={recommendTarget} onClose={() => setRecommendTarget(null)} />
      )}
      {filmDetail && (
        <FilmDetailModal movieId={filmDetail.id} initialMovie={filmDetail} onClose={() => setFilmDetail(null)} />
      )}
    </motion.div>
    </div>
    </>
  );
}

function SectionHeader({ text }) {
  return (
    <div className="flex items-center gap-2.5 px-1 mb-3">
      <p className="font-sans text-[11px] font-bold uppercase tracking-[0.25em] text-amber/50">{text}</p>
    </div>
  );
}
