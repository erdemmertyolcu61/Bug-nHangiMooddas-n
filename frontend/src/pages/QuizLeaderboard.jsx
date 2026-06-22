import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Trophy, ChevronLeft, Loader2, Crown } from 'lucide-react';
import { getDuelloLeaderboard, isLoggedIn } from '../services/api';
import { resolveAvatarUrl } from '../utils/apiConfig';
import useDocumentMeta from '../utils/useDocumentMeta';

function AvatarSmall({ user, size = 32 }) {
  const [failed, setFailed] = useState(false);
  const src = user?.avatar ? resolveAvatarUrl(
    user.avatar.startsWith('/') ? user.avatar : `/api/users/${user.user_id}/avatar`
  ) : null;

  if (!src || failed) {
    return (
      <div
        className="rounded-full bg-amber-900/60 flex items-center justify-center text-amber font-bold border border-amber/30"
        style={{ width: size, height: size, fontSize: size * 0.4 }}
      >
        {(user?.name || user?.username || '?')[0]?.toUpperCase()}
      </div>
    );
  }
  return (
    <img
      src={src} alt="" onError={() => setFailed(true)}
      className="rounded-full border border-amber/30 object-cover"
      style={{ width: size, height: size }}
    />
  );
}

export default function QuizLeaderboard() {
  useDocumentMeta({ title: 'SineQuiz Skor Tablosu' });
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoggedIn()) return;
    (async () => {
      try {
        const res = await getDuelloLeaderboard();
        setData(res);
      } catch {}
      setLoading(false);
    })();
  }, []);

  if (!isLoggedIn()) {
    return (
      <div className="min-h-screen bg-bg text-ivory">
        <div className="max-w-md mx-auto px-4 pt-20 text-center space-y-4">
          <Trophy className="mx-auto text-amber/40" size={48} />
          <h2 className="text-lg font-bold text-amber">Giriş Gerekli</h2>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 rounded-xl bg-amber-900/30 border border-amber/30 text-amber text-sm"
          >
            Ana Sayfaya Dön
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="min-h-screen bg-bg text-ivory pb-32"
    >
      <div className="max-w-md mx-auto px-4 pt-safe">
        <button
          onClick={() => navigate('/sinequiz')}
          className="mt-3 mb-3 -ml-1 flex items-center gap-1.5 text-sm text-amber/50 hover:text-amber/80 active:text-amber/90 transition-colors group min-h-[44px] min-w-[44px] px-2"
        >
          <ChevronLeft size={20} className="group-hover:-translate-x-0.5 transition-transform" /> SineQuiz
        </button>

        <div className="text-center space-y-2 mb-6">
          <div className="inline-flex items-center gap-2 text-amber">
            <Trophy size={28} />
            <h1 className="text-2xl font-bold">Skor Tablosu</h1>
          </div>
          {data?.my_rank && (
            <p className="text-sm text-amber/60">Senin sıran: <span className="text-amber font-bold">#{data.my_rank}</span></p>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="animate-spin text-amber" size={32} />
          </div>
        ) : !data?.players?.length ? (
          <div className="text-center py-16">
            <p className="text-amber/40 text-sm">Henüz sıralama yok. Oyun oynayarak sıralamaya gir!</p>
          </div>
        ) : (
          <div className="space-y-1.5">
            {data.players.map((p, i) => {
              const isMe = data.my_rank === p.rank;
              return (
                <div
                  key={p.user_id}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl border transition-all ${
                    isMe
                      ? 'border-amber/40 bg-amber/10'
                      : 'border-amber/10 bg-surface-2/30'
                  }`}
                >
                  <div className="w-7 text-center flex-shrink-0">
                    {p.rank <= 3 ? (
                      <span className="text-lg">{p.rank === 1 ? '🥇' : p.rank === 2 ? '🥈' : '🥉'}</span>
                    ) : (
                      <span className="text-xs text-amber/40 font-mono">#{p.rank}</span>
                    )}
                  </div>

                  <AvatarSmall user={p} size={36} />

                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-amber font-medium truncate">
                      {p.name || p.username}
                    </div>
                    <div className="text-[10px] text-amber/40">
                      {p.games_won}G {p.win_rate}% WR
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-0.5 flex-shrink-0">
                    <span className="text-sm font-bold text-amber">{p.elo_rating}</span>
                    <span className="text-[10px]">{p.league?.emoji} {p.league?.label}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
}
