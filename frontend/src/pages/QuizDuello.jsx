import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Swords, Trophy, Users, Check, X, ChevronLeft, Clock,
  Loader2, Crown, Zap, ArrowRight, RotateCcw,
} from 'lucide-react';
import {
  getDuelloCategories, createDuelloRoom, getDuelloState,
  joinDuelloRoom, setDuelloReady, startDuello,
  submitDuelloAnswer, getDuelloResults, leaveDuelloRoom,
  getFriends, proxyImageUrl, isLoggedIn,
} from '../services/api';
import useDuelloPoll from '../hooks/useDuelloPoll';
import { resolveAvatarUrl } from '../utils/apiConfig';
import useDocumentMeta from '../utils/useDocumentMeta';

const TOTAL_QUESTIONS = 10;
const QUESTION_TIME = 30;

function AvatarCircle({ user, size = 40 }) {
  const [failed, setFailed] = useState(false);
  const src = user?.avatar ? resolveAvatarUrl(
    user.avatar.startsWith('/') ? user.avatar : `/api/users/${user.id}/avatar`
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

// ─── INTRO: Arkadaş seçimi + kategori seçimi ──────────────────────────────

function DuelloIntro({ onCreateRoom }) {
  const [friends, setFriends] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [selectedCats, setSelectedCats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [friendSearch, setFriendSearch] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const [fr, cats] = await Promise.all([getFriends(), getDuelloCategories()]);
        setFriends(fr?.friends || []);
        setCategories(cats?.categories || []);
      } catch { setError('Veriler yüklenemedi'); }
      setLoading(false);
    })();
  }, []);

  const toggleCat = (slug) => {
    setSelectedCats(prev =>
      prev.includes(slug) ? prev.filter(s => s !== slug) : prev.length < 3 ? [...prev, slug] : prev
    );
  };

  const handleCreate = async () => {
    if (!selectedFriend || selectedCats.length !== 3) return;
    setCreating(true);
    setError('');
    try {
      const res = await createDuelloRoom(selectedFriend.id, selectedCats);
      onCreateRoom(res.room_id);
    } catch (e) {
      setError(e.message || 'Oda oluşturulamadı');
      setCreating(false);
    }
  };

  const filteredFriends = friends.filter(f =>
    !friendSearch || (f.name || '').toLowerCase().includes(friendSearch.toLowerCase())
    || (f.username || '').toLowerCase().includes(friendSearch.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-amber" size={32} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 text-amber">
          <Swords size={28} />
          <h1 className="text-2xl font-bold">Sinema Düello</h1>
        </div>
        <p className="text-sm text-amber/60">Arkadaşını seç, kategorileri belirle, düelloya başla!</p>
      </div>

      {/* Arkadaş Seçimi */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-amber/80 uppercase tracking-wider">Rakibini Seç</h2>
        {friends.length === 0 ? (
          <div className="bg-amber-900/10 border border-amber/20 rounded-2xl p-4 text-center text-amber/50 text-sm">
            Henüz arkadaşın yok. Profil sayfasından arkadaş ekle!
          </div>
        ) : (
          <>
            {friends.length > 4 && (
              <input
                type="text"
                placeholder="Arkadaş ara..."
                value={friendSearch}
                onChange={e => setFriendSearch(e.target.value)}
                className="w-full bg-black/30 border border-amber/20 rounded-xl px-3 py-2 text-sm text-amber placeholder:text-amber/30 focus:outline-none focus:border-amber/50"
              />
            )}
            <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
              {filteredFriends.map(f => (
                <button
                  key={f.id}
                  onClick={() => setSelectedFriend(f)}
                  className={`flex items-center gap-2 p-2 rounded-xl border transition-all text-left ${
                    selectedFriend?.id === f.id
                      ? 'border-amber bg-amber/15 shadow-[0_0_12px_rgba(245,158,11,0.15)]'
                      : 'border-amber/15 bg-black/20 hover:border-amber/40'
                  }`}
                >
                  <AvatarCircle user={f} size={32} />
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-amber truncate">{f.name || f.username}</div>
                    <div className="text-[10px] text-amber/40 truncate">@{f.username}</div>
                  </div>
                  {selectedFriend?.id === f.id && <Check size={14} className="text-amber ml-auto flex-shrink-0" />}
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Kategori Seçimi */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-amber/80 uppercase tracking-wider">3 Kategori Seç</h2>
          <span className="text-xs text-amber/40">{selectedCats.length}/3</span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {categories.map(cat => (
            <button
              key={cat.slug}
              onClick={() => toggleCat(cat.slug)}
              className={`flex items-center gap-2 px-3 py-2.5 rounded-xl border text-sm transition-all ${
                selectedCats.includes(cat.slug)
                  ? 'border-amber bg-amber/15 text-amber font-medium'
                  : 'border-amber/15 bg-black/20 text-amber/60 hover:border-amber/40'
              }`}
            >
              <span>{cat.emoji}</span>
              <span className="truncate">{cat.label}</span>
            </button>
          ))}
        </div>
        <p className="text-[10px] text-amber/30 text-center">+ 1 rastgele kategori otomatik eklenir</p>
      </div>

      {error && <p className="text-red-400 text-xs text-center">{error}</p>}

      {/* Başlat Butonu */}
      <button
        onClick={handleCreate}
        disabled={!selectedFriend || selectedCats.length !== 3 || creating}
        className="w-full py-3 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 text-black font-bold
                   disabled:opacity-30 disabled:cursor-not-allowed hover:shadow-[0_0_20px_rgba(245,158,11,0.3)]
                   transition-all flex items-center justify-center gap-2"
      >
        {creating ? <Loader2 className="animate-spin" size={18} /> : <Swords size={18} />}
        {creating ? 'Oda kuruluyor...' : 'Düello Daveti Gönder'}
      </button>
    </div>
  );
}

// ─── LOBBY: Bekleme odası ──────────────────────────────────────────────────

function DuelloLobby({ roomState, onReady, onStart, onLeave }) {
  if (!roomState) return null;
  const { creator, opponent, creator_ready, opponent_ready, is_creator, categories, status } = roomState;
  const bothReady = creator_ready && opponent_ready;

  return (
    <div className="space-y-6 text-center">
      <div className="space-y-1">
        <Swords className="mx-auto text-amber" size={32} />
        <h2 className="text-xl font-bold text-amber">Düello Odası</h2>
        <p className="text-xs text-amber/50">
          {!opponent ? 'Rakip bekleniyor...' : bothReady ? 'İki oyuncu da hazır!' : 'Hazır olunca butona bas'}
        </p>
      </div>

      {/* Oyuncular */}
      <div className="flex items-center justify-center gap-6">
        <div className="flex flex-col items-center gap-2">
          <div className={`p-1 rounded-full ${creator_ready ? 'ring-2 ring-green-500' : 'ring-2 ring-amber/20'}`}>
            <AvatarCircle user={creator} size={56} />
          </div>
          <span className="text-xs text-amber font-medium">{creator?.name || creator?.username}</span>
          {creator_ready && <span className="text-[10px] text-green-400">Hazır</span>}
        </div>

        <div className="text-amber/30 text-2xl font-bold">VS</div>

        <div className="flex flex-col items-center gap-2">
          {opponent ? (
            <>
              <div className={`p-1 rounded-full ${opponent_ready ? 'ring-2 ring-green-500' : 'ring-2 ring-amber/20'}`}>
                <AvatarCircle user={opponent} size={56} />
              </div>
              <span className="text-xs text-amber font-medium">{opponent?.name || opponent?.username}</span>
              {opponent_ready && <span className="text-[10px] text-green-400">Hazır</span>}
            </>
          ) : (
            <>
              <div className="w-14 h-14 rounded-full bg-amber-900/20 border-2 border-dashed border-amber/20 flex items-center justify-center">
                <Loader2 className="animate-spin text-amber/30" size={20} />
              </div>
              <span className="text-xs text-amber/40">Bekleniyor...</span>
            </>
          )}
        </div>
      </div>

      {/* Kategoriler */}
      <div className="flex flex-wrap justify-center gap-2">
        {(categories || []).map((cat, i) => (
          <span key={i} className="px-2 py-1 rounded-lg bg-amber-900/20 border border-amber/15 text-xs text-amber/70">
            {cat.emoji} {cat.label}
          </span>
        ))}
      </div>

      {/* Butonlar */}
      <div className="space-y-3">
        {opponent && (
          <button
            onClick={onReady}
            className={`w-full py-3 rounded-2xl font-bold transition-all ${
              (is_creator ? creator_ready : opponent_ready)
                ? 'bg-green-600/80 text-white'
                : 'bg-amber-900/30 border border-amber/30 text-amber hover:bg-amber-900/50'
            }`}
          >
            {(is_creator ? creator_ready : opponent_ready) ? '✓ Hazırım' : 'Hazır Ol'}
          </button>
        )}

        {is_creator && bothReady && (
          <button
            onClick={onStart}
            className="w-full py-3 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 text-black font-bold
                       hover:shadow-[0_0_20px_rgba(245,158,11,0.3)] transition-all flex items-center justify-center gap-2"
          >
            <Zap size={18} /> Düelloyu Başlat!
          </button>
        )}

        <button onClick={onLeave} className="text-xs text-amber/30 hover:text-amber/60 transition-colors">
          Odadan Ayrıl
        </button>
      </div>
    </div>
  );
}

// ─── GAME: Aktif quiz ──────────────────────────────────────────────────────

function DuelloGame({ roomState, onAnswer }) {
  const { question, my_answer, opponent_answered, scores, current_question, total_questions } = roomState;
  const [timeLeft, setTimeLeft] = useState(QUESTION_TIME);
  const [selected, setSelected] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const timerRef = useRef(null);
  const lastQIdx = useRef(-1);

  useEffect(() => {
    if (!question) return;
    if (question.index !== lastQIdx.current) {
      lastQIdx.current = question.index;
      setSelected(null);
      setSubmitting(false);
      const serverRemaining = Math.ceil((question.time_remaining_ms || QUESTION_TIME * 1000) / 1000);
      setTimeLeft(Math.min(QUESTION_TIME, Math.max(0, serverRemaining)));
    }
  }, [question]);

  useEffect(() => {
    if (my_answer || !question) return;
    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [question?.index, my_answer]);

  const handleSelect = async (option) => {
    if (selected || my_answer || timeLeft <= 0 || submitting) return;
    setSelected(option);
    setSubmitting(true);
    clearInterval(timerRef.current);
    await onAnswer(question.index, option);
    setSubmitting(false);
  };

  if (!question) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-amber" size={32} />
      </div>
    );
  }

  const isBlurPoster = question.extra_data?.blur;
  const timerPct = (timeLeft / QUESTION_TIME) * 100;
  const timerColor = timeLeft > 10 ? 'text-green-400' : timeLeft > 5 ? 'text-yellow-400' : 'text-red-400';

  return (
    <div className="space-y-4">
      {/* Header: skor + soru sayacı */}
      <div className="flex items-center justify-between text-xs">
        <div className="text-amber/60">
          <span className="text-amber font-bold">{scores?.me || 0}</span> puan
        </div>
        <div className="text-amber/80 font-medium">
          {(current_question || 0) + 1} / {total_questions || TOTAL_QUESTIONS}
        </div>
        <div className="text-amber/60">
          Rakip: <span className="font-bold">{scores?.opponent || 0}</span>
        </div>
      </div>

      {/* Timer bar */}
      <div className="relative h-1.5 bg-amber-900/20 rounded-full overflow-hidden">
        <motion.div
          className={`absolute inset-y-0 left-0 rounded-full ${
            timeLeft > 10 ? 'bg-green-500' : timeLeft > 5 ? 'bg-yellow-500' : 'bg-red-500'
          }`}
          initial={false}
          animate={{ width: `${timerPct}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      {/* Timer + rakip durumu */}
      <div className="flex items-center justify-between">
        <div className={`flex items-center gap-1 text-sm font-mono font-bold ${timerColor}`}>
          <Clock size={14} />
          {timeLeft}s
        </div>
        {opponent_answered && !my_answer && (
          <span className="text-xs text-amber/40 animate-pulse">Rakip cevapladı!</span>
        )}
      </div>

      {/* Soru görseli */}
      {question.hint_image && (
        <div className="flex justify-center">
          <img
            src={proxyImageUrl(question.hint_image)}
            alt=""
            className={`rounded-xl border border-amber/15 max-h-48 object-contain ${isBlurPoster ? 'blur-lg hover:blur-md transition-all duration-1000' : ''}`}
            style={isBlurPoster ? {
              filter: `blur(${Math.max(2, timeLeft * 0.6)}px)`,
              transition: 'filter 1s ease',
            } : {}}
          />
        </div>
      )}

      {/* Soru metni */}
      <p className="text-center text-amber font-medium text-sm leading-relaxed whitespace-pre-line">
        {question.text}
      </p>

      {/* Seçenekler */}
      <div className="grid grid-cols-1 gap-2">
        {(question.options || []).map((option, i) => {
          const isSelected = selected === option || my_answer?.selected === option;
          const isCorrect = my_answer && option === my_answer.selected && my_answer.is_correct;
          const isWrong = my_answer && option === my_answer.selected && !my_answer.is_correct;
          const showCorrectHighlight = my_answer && !my_answer.is_correct && option === question.options.find(
            o => my_answer.correct_answer ? o === my_answer.correct_answer : false
          );

          return (
            <motion.button
              key={`${question.index}-${i}`}
              onClick={() => handleSelect(option)}
              disabled={!!my_answer || !!selected || timeLeft <= 0}
              whileTap={!my_answer && !selected && timeLeft > 0 ? { scale: 0.97 } : {}}
              className={`w-full px-4 py-3 rounded-xl border text-sm text-left transition-all ${
                isCorrect
                  ? 'border-green-500 bg-green-500/20 text-green-300'
                  : isWrong
                    ? 'border-red-500 bg-red-500/20 text-red-300'
                    : isSelected
                      ? 'border-amber bg-amber/20 text-amber'
                      : 'border-amber/15 bg-black/20 text-amber/80 hover:border-amber/40 hover:bg-amber-900/10'
              } disabled:cursor-default`}
            >
              <div className="flex items-center justify-between">
                <span>{option}</span>
                {isCorrect && <Check size={16} className="text-green-400" />}
                {isWrong && <X size={16} className="text-red-400" />}
              </div>
            </motion.button>
          );
        })}
      </div>

      {/* Cevap sonrası bilgi */}
      {my_answer && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`text-center text-sm py-2 rounded-xl ${
            my_answer.is_correct ? 'text-green-400' : 'text-red-400'
          }`}
        >
          {my_answer.is_correct
            ? `Doğru! +${my_answer.score} puan`
            : 'Yanlış!'}
          {!opponent_answered && (
            <span className="block text-xs text-amber/40 mt-1">Rakip bekleniyor...</span>
          )}
        </motion.div>
      )}
    </div>
  );
}

// ─── RESULTS: Oyun sonu ────────────────────────────────────────────────────

function DuelloResults({ roomId, onPlayAgain, onGoHome }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getDuelloResults(roomId);
        setResults(data);
      } catch {}
      setLoading(false);
    })();
  }, [roomId]);

  if (loading || !results) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-amber" size={32} />
      </div>
    );
  }

  const { creator, opponent, winner_id, is_draw, questions } = results;
  const iWon = winner_id === (creator?.id);
  const winner = winner_id === creator?.id ? creator : opponent;
  const loser = winner_id === creator?.id ? opponent : creator;

  return (
    <div className="space-y-6">
      {/* Kazanan banner */}
      <div className="text-center space-y-3">
        {is_draw ? (
          <>
            <div className="text-4xl">🤝</div>
            <h2 className="text-xl font-bold text-amber">Berabere!</h2>
          </>
        ) : (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', bounce: 0.5 }}
              className="text-5xl"
            >
              🏆
            </motion.div>
            <h2 className="text-xl font-bold text-amber">
              {winner?.name || winner?.username} Kazandı!
            </h2>
          </>
        )}
      </div>

      {/* Skor karşılaştırma */}
      <div className="flex items-center justify-center gap-4">
        <div className="flex flex-col items-center gap-2 flex-1">
          <AvatarCircle user={creator} size={48} />
          <span className="text-xs text-amber/70">{creator?.name || creator?.username}</span>
          <div className={`text-2xl font-bold ${winner_id === creator?.id ? 'text-amber' : 'text-amber/50'}`}>
            {creator?.total_score || 0}
          </div>
          <span className="text-[10px] text-amber/40">{creator?.total_correct || 0}/{TOTAL_QUESTIONS} doğru</span>
        </div>

        <div className="text-amber/20 font-bold text-lg">–</div>

        <div className="flex flex-col items-center gap-2 flex-1">
          <AvatarCircle user={opponent} size={48} />
          <span className="text-xs text-amber/70">{opponent?.name || opponent?.username}</span>
          <div className={`text-2xl font-bold ${winner_id === opponent?.id ? 'text-amber' : 'text-amber/50'}`}>
            {opponent?.total_score || 0}
          </div>
          <span className="text-[10px] text-amber/40">{opponent?.total_correct || 0}/{TOTAL_QUESTIONS} doğru</span>
        </div>
      </div>

      {/* Soru detayları */}
      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-amber/60 uppercase tracking-wider">Soru Detayları</h3>
        <div className="space-y-1.5 max-h-64 overflow-y-auto">
          {(questions || []).map((q, i) => {
            const ca = q.creator_answer;
            const oa = q.opponent_answer;
            return (
              <div key={i} className="bg-black/20 border border-amber/10 rounded-xl px-3 py-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="text-xs text-amber/70 flex-1 min-w-0">
                    <span className="text-amber/40 mr-1">S{i + 1}.</span>
                    {q.text?.split('\n')[0]?.slice(0, 60)}
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className={`text-xs ${ca?.is_correct ? 'text-green-400' : 'text-red-400'}`}>
                      {ca?.is_correct ? `✓${ca.score}` : '✗'}
                    </span>
                    <span className="text-amber/20">|</span>
                    <span className={`text-xs ${oa?.is_correct ? 'text-green-400' : 'text-red-400'}`}>
                      {oa?.is_correct ? `✓${oa.score}` : '✗'}
                    </span>
                  </div>
                </div>
                <div className="text-[10px] text-amber/30 mt-0.5">Doğru: {q.correct_answer}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Butonlar */}
      <div className="space-y-2">
        <button
          onClick={onPlayAgain}
          className="w-full py-3 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 text-black font-bold
                     hover:shadow-[0_0_20px_rgba(245,158,11,0.3)] transition-all flex items-center justify-center gap-2"
        >
          <RotateCcw size={16} /> Rövanş!
        </button>
        <button
          onClick={onGoHome}
          className="w-full py-2.5 rounded-2xl border border-amber/20 text-amber/60 text-sm hover:bg-amber-900/10 transition-all"
        >
          Ana Sayfaya Dön
        </button>
      </div>
    </div>
  );
}

// ─── EMBEDDABLE DUELLO CONTENT ────────────────────────────────────────────

export function DuelloContent({ initialRoomId = null }) {
  const navigate = useNavigate();

  const [phase, setPhase] = useState(initialRoomId ? 'lobby' : 'intro');
  const [roomId, setRoomId] = useState(initialRoomId);
  const [startingGame, setStartingGame] = useState(false);
  const [joinError, setJoinError] = useState('');

  useEffect(() => {
    if (initialRoomId && initialRoomId !== roomId) {
      setRoomId(initialRoomId);
      setPhase('lobby');
    }
  }, [initialRoomId]);

  const isPlaying = phase === 'lobby' || phase === 'playing';
  const { state: roomState, error: pollError, refetch } = useDuelloPoll(
    roomId, isPlaying, phase === 'playing' ? 2500 : 3500
  );

  useEffect(() => {
    if (initialRoomId && phase === 'lobby' && !roomState) {
      (async () => {
        try {
          await joinDuelloRoom(initialRoomId);
        } catch (e) {
          if (!e.message?.includes('Kendi odana')) {
            setJoinError(e.message);
          }
        }
      })();
    }
  }, [initialRoomId]);

  useEffect(() => {
    if (!roomState) return;
    if (roomState.status === 'PLAYING' && phase !== 'playing') {
      setPhase('playing');
    } else if (roomState.status === 'FINISHED' && phase !== 'results') {
      setPhase('results');
    } else if (roomState.status === 'ABANDONED') {
      setPhase('intro');
      setRoomId(null);
    }
  }, [roomState?.status]);

  const handleCreateRoom = (newRoomId) => {
    setRoomId(newRoomId);
    setPhase('lobby');
    window.history.replaceState({}, '', `/kafan-mi-karisik?tab=duello&room=${newRoomId}`);
  };

  const handleReady = async () => {
    await setDuelloReady(roomId);
    refetch();
  };

  const handleStart = async () => {
    setStartingGame(true);
    try {
      await startDuello(roomId);
      refetch();
    } catch (e) {
      setStartingGame(false);
    }
  };

  const handleLeave = async () => {
    await leaveDuelloRoom(roomId);
    setRoomId(null);
    setPhase('intro');
    window.history.replaceState({}, '', '/kafan-mi-karisik?tab=duello');
  };

  const handleAnswer = async (questionIndex, answer) => {
    const result = await submitDuelloAnswer(roomId, questionIndex, answer);
    if (result) {
      setTimeout(refetch, 300);
    }
    return result;
  };

  const handlePlayAgain = () => {
    setRoomId(null);
    setPhase('intro');
    window.history.replaceState({}, '', '/kafan-mi-karisik?tab=duello');
  };

  if (!isLoggedIn()) {
    return (
      <div className="max-w-md mx-auto px-4 pt-12 text-center space-y-4">
        <Swords className="mx-auto text-amber/40" size={48} />
        <h2 className="text-lg font-bold text-amber">Giriş Gerekli</h2>
        <p className="text-sm text-amber/50">Sinema Düello oynamak için giriş yapmalısın.</p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto">
      {phase !== 'intro' && phase !== 'playing' && (
        <button
          onClick={handleLeave}
          className="mb-4 flex items-center gap-1 text-xs text-amber/40 hover:text-amber/70 transition-colors"
        >
          <ChevronLeft size={14} />
          Odadan Ayrıl
        </button>
      )}

      {joinError && (
        <div className="mb-4 p-3 rounded-xl bg-red-900/20 border border-red-500/30 text-red-400 text-xs text-center">
          {joinError}
        </div>
      )}

      <AnimatePresence mode="wait">
        {phase === 'intro' && (
          <motion.div
            key="intro"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <DuelloIntro onCreateRoom={handleCreateRoom} />
          </motion.div>
        )}

        {phase === 'lobby' && (
          <motion.div
            key="lobby"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <DuelloLobby
              roomState={roomState}
              onReady={handleReady}
              onStart={handleStart}
              onLeave={handleLeave}
            />
          </motion.div>
        )}

        {phase === 'playing' && roomState && (
          <motion.div
            key="playing"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <DuelloGame
              roomState={roomState}
              onAnswer={handleAnswer}
            />
          </motion.div>
        )}

        {phase === 'results' && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <DuelloResults
              roomId={roomId}
              onPlayAgain={handlePlayAgain}
              onGoHome={() => navigate('/kafan-mi-karisik')}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ─── REDIRECT WRAPPER (eski /duello route'u için) ─────────────────────────

export default function QuizDuello() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const roomParam = searchParams.get('room');

  useEffect(() => {
    const url = roomParam
      ? `/kafan-mi-karisik?tab=duello&room=${roomParam}`
      : '/kafan-mi-karisik?tab=duello';
    navigate(url, { replace: true });
  }, []);

  return null;
}
