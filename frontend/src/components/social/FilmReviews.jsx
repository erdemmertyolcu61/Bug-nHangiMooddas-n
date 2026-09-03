import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Quote, MoreHorizontal, Flag, Trash2, PenLine, EyeOff } from 'lucide-react';
import { getMovieReviews, deleteMovieReview, isLoggedIn } from '../../services/api';
import { resolveAvatarUrl } from '../../utils/apiConfig';
import { useAuth } from '../../context/AuthContext';
import ReviewComposerSheet from './ReviewComposerSheet';
import ReportSheet from './ReportSheet';

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const d = new Date(String(dateStr).replace(' ', 'T'));
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 3600) return 'az önce';
  if (diff < 86400) return `${Math.floor(diff / 3600)}sa`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}g`;
  return new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'short' }).format(d);
}



export default function FilmReviews({ movie }) {
  const movieId = movie?.id || movie?.tmdb_id;
  const loggedIn = isLoggedIn();
  const { user: authUser } = useAuth();
  const [reviews, setReviews] = useState(null);
  const [composerOpen, setComposerOpen] = useState(false);
  const [reportTarget, setReportTarget] = useState(null);
  const [menuFor, setMenuFor] = useState(null);
  const [revealed, setRevealed] = useState(new Set());

  const load = useCallback(async () => {
    if (!movieId) return;
    const data = await getMovieReviews(movieId);
    if (data) setReviews(data.reviews || []);
  }, [movieId]);

  useEffect(() => {
    let alive = true;
    (async () => {
      if (!movieId) return;
      const data = await getMovieReviews(movieId);
      if (alive && data) setReviews(data.reviews || []);
    })();
    return () => { alive = false; };
  }, [movieId]);

  const mine = reviews?.find((r) => r.is_mine);

  const handleReviewSaved = useCallback((review) => {
    setReviews((prev) => {
      const others = (prev || []).filter((r) => !r.is_mine);
      const entry = {
        id: review.id || `temp-${Date.now()}`,
        tmdb_id: review.tmdb_id || movieId,
        user_id: review.user_id || authUser?.id || 0,
        content: review.content || '',
        has_spoiler: review.has_spoiler || false,
        created_at: review.created_at || new Date().toISOString(),
        username: review.username || authUser?.username || authUser?.name || '',
        avatar: review.avatar || authUser?.picture || '',
        like_count: review.like_count || 0,
        liked_by_me: review.liked_by_me || false,
        is_mine: true,
      };
      return [entry, ...others];
    });
    setComposerOpen(false);
  }, [movieId, authUser]);

  const handleDelete = async () => {
    setMenuFor(null);
    try {
      await deleteMovieReview(movieId);
      setReviews((rs) => (rs || []).filter((r) => !r.is_mine));
    } catch {
      // Silme başarısız olursa listeyi yeniden yükle
      load();
    }
  };

  const onBlocked = (blockedUserId) => {
    setReviews((rs) => rs.filter((r) => r.user_id !== blockedUserId));
    setReportTarget(null);
  };

  if (!movieId) return null;

  return (
    <section className="mt-6">
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <Quote size={14} className="text-amber/60 shrink-0" />
          <p className="font-sans text-[11px] font-bold uppercase tracking-[0.2em] text-amber/50 truncate">
            Topluluk Sözleri{reviews?.length > 0 ? ` · ${reviews.length}` : ''}
          </p>
        </div>
        {loggedIn && (
          <button onClick={() => setComposerOpen(true)}
            className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber/12 border border-amber/25 text-amber
                       text-[10px] font-bold uppercase tracking-wider hover:bg-amber/20 transition-all whitespace-nowrap">
            <PenLine size={11} /> {mine ? 'Düzenle' : 'Söz Bırak'}
          </button>
        )}
      </div>

      {reviews === null ? (
        <div className="space-y-2">
          {[0, 1].map((i) => <div key={i} className="h-16 rounded-2xl bg-white/5 animate-pulse" />)}
        </div>
      ) : reviews.length === 0 ? (
        <p className="text-sm sm:text-[13px] font-serif italic text-white/35 py-2">
          Bu film için henüz söz söylenmemiş. {loggedIn ? 'İlk sözü sen bırak.' : 'Giriş yap, ilk sözü sen bırak.'}
        </p>
      ) : (
        <div className="space-y-2.5">
          {reviews.map((r, i) => {
            const spoilerHidden = r.has_spoiler && !revealed.has(r.id);
            return (
              <motion.div key={r.id}
                initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="relative p-3 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
                {/* Başlık: avatar + ad/zaman/spoiler + menü */}
                <div className="flex items-center gap-2.5">
                  <span className="w-8 h-8 rounded-full overflow-hidden bg-white/10 shrink-0 ring-1 ring-amber/15">
                    {r.avatar
                      ? <img src={resolveAvatarUrl(r.avatar)} alt="" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                      : <span className="w-full h-full flex items-center justify-center text-[12px] font-serif font-bold text-amber/70">{(r.username || '?')[0].toUpperCase()}</span>}
                  </span>
                  <div className="flex-1 min-w-0 flex items-center gap-1.5 flex-wrap">
                    <p className="text-[13px] sm:text-[12px] font-semibold text-amber/75 truncate max-w-[160px]">@{r.username}</p>
                    <span className="text-[10px] text-white/25">{timeAgo(r.created_at)}</span>
                    {r.has_spoiler && (
                      <span className="text-[9px] font-bold uppercase tracking-wider text-rose-400/70 bg-rose-500/10 px-1.5 py-0.5 rounded-full">
                        ⚠ Spoiler
                      </span>
                    )}
                  </div>
                  <div className="relative shrink-0 ml-auto">
                    <button onClick={() => setMenuFor(menuFor === r.id ? null : r.id)}
                      aria-label="Seçenekler"
                      className="p-1.5 -mr-1 rounded-full hover:bg-white/10 transition-all">
                      <MoreHorizontal size={15} className="text-white/40" />
                    </button>
                    {menuFor === r.id && (
                      <div className="absolute right-0 top-8 z-30 min-w-[140px] py-1 rounded-xl bg-[#221a16] border border-white/10 shadow-2xl">
                        {r.is_mine ? (
                          <button onClick={handleDelete}
                            className="w-full flex items-center gap-2 px-3.5 py-2.5 text-[12px] text-rose-400/90 hover:bg-white/5 transition-all">
                            <Trash2 size={13} /> Sözü Sil
                          </button>
                        ) : (
                          <button onClick={() => { setMenuFor(null); setReportTarget(r); }}
                            className="w-full flex items-center gap-2 px-3.5 py-2.5 text-[12px] text-ivory/80 hover:bg-white/5 transition-all">
                            <Flag size={13} /> Bildir / Engelle
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* İçerik (avatarın altına hizalı) */}
                <div className="mt-1.5 pl-[42px]">
                  {spoilerHidden ? (
                    <button onClick={() => setRevealed((s) => new Set(s).add(r.id))}
                      className="w-full text-left rounded-xl border border-rose-400/30 bg-rose-500/[0.07] px-3 py-2.5 transition-colors hover:bg-rose-500/[0.12]">
                      <p className="text-[13px] font-serif text-fg/85 blur-[6px] select-none line-clamp-2" aria-hidden>{r.content}</p>
                      <span className="mt-1.5 inline-flex items-center gap-1.5 text-[11px] sm:text-[10px] font-bold uppercase tracking-wider text-rose-500/90">
                        <EyeOff size={12} className="shrink-0" /> Spoiler · görmek için dokun
                      </span>
                    </button>
                  ) : (
                    <p className="text-sm sm:text-[13.5px] font-serif text-fg/90 leading-snug break-words whitespace-pre-wrap">{r.content}</p>
                  )}
                </div>


              </motion.div>
            );
          })}
        </div>
      )}

      {composerOpen && (
        <ReviewComposerSheet
          movie={movie}
          initialContent={mine?.content || ''}
          initialSpoiler={mine?.has_spoiler || false}
          onClose={() => setComposerOpen(false)}
          onSaved={handleReviewSaved}
        />
      )}

      {reportTarget && (
        <ReportSheet
          contentType="review"
          contentId={reportTarget.id}
          author={{ id: reportTarget.user_id, username: reportTarget.username }}
          onClose={() => setReportTarget(null)}
          onBlocked={onBlocked}
        />
      )}
    </section>
  );
}
