import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Swords, Trophy, Users, Check, X, ChevronLeft, Clock, Zap, Snowflake, Dices, Scissors,
  Loader2, ArrowRight, RotateCcw, Image,
} from 'lucide-react';
import {
  getDuelloCategories, createDuelloRoom,
  joinDuelloRoom, setDuelloReady, startDuello,
  submitDuelloAnswer, getDuelloResults, leaveDuelloRoom, rematchDuello,
  isLoggedIn, callDuelloJoker,
  joinMatchmaking, pollMatchmaking, leaveMatchmaking,
} from '../services/api';
import useDuelloPoll from '../hooks/useDuelloPoll';
import useQuizSounds from '../hooks/useQuizSounds';
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

// ─── INTRO: Oda oluştur veya koda katıl ──────────────────────────────────

function DuelloIntro({ onCreateRoom, onJoinRoom, onNavigateLeaderboard }) {
  const [categories, setCategories] = useState([]);
  const [selectedCats, setSelectedCats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchElapsed, setSearchElapsed] = useState(0);
  const searchIntervalRef = useRef(null);
  const searchPollRef = useRef(null);

  useEffect(() => {
    (async () => {
      try {
        const cats = await getDuelloCategories();
        setCategories(cats?.categories || []);
      } catch { setError('Kategoriler yüklenemedi'); }
      setLoading(false);
    })();
  }, []);

  const toggleCat = (slug) => {
    setSelectedCats(prev =>
      prev.includes(slug) ? prev.filter(s => s !== slug) : prev.length < 3 ? [...prev, slug] : prev
    );
  };

  const handleCreate = async () => {
    if (selectedCats.length === 0 || selectedCats.length > 3) return;
    setCreating(true);
    setError('');
    try {
      const res = await createDuelloRoom(selectedCats);
      onCreateRoom(res.room_id);
    } catch (e) {
      setError(e.message || 'Oda oluşturulamadı');
      setCreating(false);
    }
  };

  const handleJoin = async () => {
    const code = joinCode.trim().toUpperCase();
    if (code.length < 4) return;
    setJoining(true);
    setError('');
    try {
      await joinDuelloRoom(code);
      onJoinRoom(code);
    } catch (e) {
      setError(e.message || 'Odaya katılınamadı');
      setJoining(false);
    }
  };

  const stopSearch = useCallback(() => {
    clearInterval(searchIntervalRef.current);
    clearInterval(searchPollRef.current);
    setSearching(false);
    setSearchElapsed(0);
  }, []);

  const handleFindMatch = async () => {
    if (selectedCats.length === 0 || selectedCats.length > 3) return;
    setSearching(true);
    setError('');
    setSearchElapsed(0);
    try {
      const res = await joinMatchmaking(selectedCats);
      if (res.matched) {
        stopSearch();
        onJoinRoom(res.room_id);
        return;
      }
      searchIntervalRef.current = setInterval(() => setSearchElapsed(p => p + 1), 1000);
      searchPollRef.current = setInterval(async () => {
        try {
          const poll = await pollMatchmaking();
          if (poll.matched) {
            stopSearch();
            onJoinRoom(poll.room_id);
          } else if (poll.timeout) {
            stopSearch();
            setError('Rakip bulunamadı, tekrar dene.');
          }
        } catch {
          stopSearch();
          setError('Eşleşme hatası');
        }
      }, 2000);
    } catch (e) {
      setSearching(false);
      setError(e.message || 'Eşleşme başlatılamadı');
    }
  };

  const handleCancelSearch = async () => {
    stopSearch();
    try { await leaveMatchmaking(); } catch {}
  };

  useEffect(() => () => { clearInterval(searchIntervalRef.current); clearInterval(searchPollRef.current); }, []);

  if (searching) {
    return (
      <div className="flex flex-col items-center justify-center py-16 space-y-6">
        <div className="relative">
          <div className="w-24 h-24 rounded-full border-4 border-amber/20 flex items-center justify-center">
            <Users className="text-amber" size={36} />
          </div>
          <div className="absolute inset-0 w-24 h-24 rounded-full border-4 border-t-amber border-r-transparent border-b-transparent border-l-transparent animate-spin" />
        </div>
        <div className="text-center space-y-1">
          <p className="text-amber font-bold text-lg">Rakip aranıyor...</p>
          <p className="text-amber/50 text-sm font-mono">{searchElapsed}s</p>
        </div>
        <button
          onClick={handleCancelSearch}
          className="px-6 py-2.5 rounded-xl border border-amber/30 text-amber/70 text-sm hover:bg-amber/10 transition-all"
        >
          İptal
        </button>
      </div>
    );
  }

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
          <h1 className="text-2xl font-bold">SineQuiz</h1>
        </div>
        <p className="text-sm text-amber/60">Oda kur veya arkadaşının kodunu gir!</p>
      </div>

      {/* Oda Koduna Katıl */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-amber/80 uppercase tracking-wider">Oda Koduna Katıl</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Oda kodu gir..."
            value={joinCode}
            onChange={e => setJoinCode(e.target.value.toUpperCase())}
            maxLength={8}
            className="flex-1 min-w-0 bg-surface-2/50 border border-amber/20 rounded-xl px-4 py-3 text-sm text-amber font-mono font-bold tracking-[0.3em] text-center uppercase placeholder:text-fg-subtle placeholder:tracking-normal placeholder:font-normal focus:outline-none focus:border-amber/50"
            onKeyDown={e => { if (e.key === 'Enter') handleJoin(); }}
          />
          <button
            onClick={handleJoin}
            disabled={joinCode.trim().length < 4 || joining}
            className="shrink-0 whitespace-nowrap px-5 py-3 rounded-xl bg-amber-600 text-black font-bold text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:bg-amber-500 transition-all flex items-center gap-1.5"
          >
            {joining ? <Loader2 className="animate-spin" size={16} /> : <ArrowRight size={16} />}
            Katıl
          </button>
        </div>
      </div>

      {/* Ayırıcı */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-px bg-amber/15" />
        <span className="text-xs text-amber/30 font-bold uppercase">veya oda kur</span>
        <div className="flex-1 h-px bg-amber/15" />
      </div>

      {/* Kategori Seçimi */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-amber/80 uppercase tracking-wider">Kategori Seç</h2>
          <span className="text-xs text-amber/40">{selectedCats.length}/3</span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {categories.map(cat => (
            <button
              key={cat.slug}
              onClick={() => toggleCat(cat.slug)}
              className={`px-3 py-2.5 rounded-xl border text-sm transition-all ${
                selectedCats.includes(cat.slug)
                  ? 'border-amber bg-amber/15 text-amber font-medium'
                  : 'border-amber/15 bg-surface-2/30 text-fg-muted hover:border-amber/40'
              }`}
            >
              <span className="truncate">{cat.label}</span>
            </button>
          ))}
          <button
            key="rastgele"
            onClick={() => toggleCat("rastgele")}
            className={`px-3 py-2.5 rounded-xl border text-sm transition-all ${
              selectedCats.includes("rastgele")
                ? 'border-amber bg-amber/15 text-amber font-medium'
                : 'border-amber/15 bg-surface-2/30 text-fg-muted hover:border-amber/40'
            }`}
          >
            <span className="truncate">Rastgele</span>
          </button>
        </div>
      </div>

      {error && <p className="text-red-400 text-xs text-center">{error}</p>}

      {/* Oda Kur Butonu */}
      <button
        onClick={handleCreate}
        disabled={selectedCats.length === 0 || selectedCats.length > 3 || creating}
        className="w-full h-12 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 text-black font-bold
                   disabled:opacity-30 disabled:cursor-not-allowed hover:shadow-[0_0_20px_rgba(245,158,11,0.3)]
                   transition-all flex items-center justify-center gap-2 whitespace-nowrap"
      >
        {creating ? <Loader2 className="animate-spin" size={18} /> : <Swords size={18} />}
        {creating ? 'Oda kuruluyor...' : 'Oda Kur'}
      </button>

      {/* Rakip Bul Butonu */}
      <button
        onClick={handleFindMatch}
        disabled={selectedCats.length === 0 || selectedCats.length > 3}
        className="w-full h-12 rounded-2xl border-2 border-amber/40 text-amber font-bold
                   disabled:opacity-30 disabled:cursor-not-allowed hover:bg-amber/10
                   transition-all flex items-center justify-center gap-2 whitespace-nowrap"
      >
        <Users size={18} />
        Rakip Bul
      </button>

      {/* Skor Tablosu */}
      <button
        onClick={onNavigateLeaderboard}
        className="w-full py-2.5 rounded-xl text-amber/60 text-sm hover:text-amber hover:bg-amber/5 transition-all flex items-center justify-center gap-2"
      >
        <Trophy size={16} />
        Skor Tablosu
      </button>
    </div>
  );
}

// ─── LOBBY: Bekleme odası ──────────────────────────────────────────────────

function DuelloLobby({ roomId, roomState, onReady, onStart, onLeave, starting }) {
  if (!roomState) {
    return (
      <div className="space-y-6 text-center">
        <div className="space-y-1">
          <Swords className="mx-auto text-amber" size={32} />
          <h2 className="text-xl font-bold text-amber">Oda Kuruluyor</h2>
        </div>
        {roomId && (
          <div className="space-y-2">
            <p className="text-xs text-amber/50">Oda kodunu arkadaşınla paylaş</p>
            <div className="inline-block bg-surface-2/60 border-2 border-amber/40 rounded-2xl px-8 py-4">
              <span className="text-3xl font-mono font-bold text-amber tracking-[0.4em]">{roomId}</span>
            </div>
          </div>
        )}
        <div className="flex items-center justify-center gap-2 text-amber/40">
          <Loader2 className="animate-spin" size={16} />
          <span className="text-sm">Bağlanıyor...</span>
        </div>
        <button onClick={onLeave} className="text-xs text-amber/30 hover:text-amber/60 transition-colors">
          Odadan Ayrıl
        </button>
      </div>
    );
  }

  const { creator, opponent, creator_ready, opponent_ready, is_creator, categories } = roomState;
  const bothReady = creator_ready && opponent_ready;

  return (
    <div className="space-y-6 text-center">
      <div className="space-y-1">
        <Swords className="mx-auto text-amber" size={32} />
        <h2 className="text-xl font-bold text-amber">SineQuiz Odası</h2>
        <p className="text-xs text-amber/50">
          {!opponent ? 'Rakip bekleniyor...' : bothReady ? 'İki oyuncu da hazır!' : 'Hazır olunca butona bas'}
        </p>
      </div>

      {/* Oda Kodu */}
      {roomId && (
        <div className="space-y-1">
          <p className="text-[10px] text-amber/40 uppercase tracking-wider">Oda Kodu</p>
          <div className="inline-block bg-surface-2/60 border-2 border-amber/40 rounded-2xl px-6 py-3">
            <span className="text-2xl font-mono font-bold text-amber tracking-[0.4em]">{roomId}</span>
          </div>
        </div>
      )}

      {/* Oyuncular */}
      <div className="flex items-center justify-center gap-6">
        <div className="flex flex-col items-center gap-2">
          <div className={`p-1 rounded-full ${creator_ready ? 'ring-2 ring-green-500' : 'ring-2 ring-amber/20'}`}>
            <AvatarCircle user={creator} size={56} />
          </div>
          <span className="text-xs text-amber font-medium">{creator?.name || creator?.username}</span>
          {creator?.league && (
            <span className="text-[10px] text-amber/50">{creator.league.emoji} {creator.league.label}</span>
          )}
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
              {opponent?.league && (
                <span className="text-[10px] text-amber/50">{opponent.league.emoji} {opponent.league.label}</span>
              )}
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
            {cat.label}
          </span>
        ))}
      </div>

      {/* Nasıl Oynanır */}
      <div className="rounded-2xl border border-amber/10 bg-surface-2/30 p-4 text-left space-y-3">
        <h3 className="text-xs font-bold text-amber uppercase tracking-wider flex items-center gap-1.5">
          <Swords size={12} /> Nasıl Oynanır?
        </h3>
        <div className="space-y-2 text-xs text-fg-muted leading-relaxed">
          <p>10 soru, her biri 30 saniye. Hızlı ve doğru cevapla daha çok puan kazan (10-20 puan).</p>
          <div className="space-y-1.5">
            <p className="font-semibold text-fg">Jokerler <span className="font-normal text-fg-muted">(oyun başına 1 kez)</span></p>
            <div className="flex items-start gap-2">
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-amber/10 border border-amber/20 shrink-0">
                <Scissors size={12} className="text-amber" />
              </span>
              <span><strong className="text-fg">Yarı Yarıya</strong> — 2 yanlış seçenek elenir</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-blue-500/10 border border-blue-500/20 shrink-0">
                <Snowflake size={12} className="text-blue-400" />
              </span>
              <span><strong className="text-fg">Süre Dondur</strong> — +10 saniye ekler</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-emerald/10 border border-emerald/20 shrink-0">
                <Dices size={12} className="text-emerald" />
              </span>
              <span><strong className="text-fg">Çifte Şans</strong> — yanlış bilirsen tekrar dene</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-purple-500/10 border border-purple-500/20 shrink-0">
                <Image size={12} className="text-purple-400" />
              </span>
              <span><strong className="text-fg">Poster İpucu</strong> — filmin posteri bulanık gösterilir</span>
            </div>
          </div>
          <p className="text-fg-subtle">Art arda 3 doğru = <strong className="text-amber">x1.5 Puan Serisi!</strong></p>
        </div>
      </div>

      {/* Butonlar */}
      <div className="space-y-3">
        {opponent && (
          <button
            onClick={onReady}
            className={`w-full py-3.5 rounded-2xl font-bold transition-all active:scale-[0.97] ${
              (is_creator ? creator_ready : opponent_ready)
                ? 'bg-green-600/80 text-white shadow-[0_4px_16px_rgba(34,197,94,0.25)]'
                : 'bg-amber-900/30 border border-amber/30 text-amber hover:bg-amber-900/50 hover:shadow-[0_4px_16px_rgba(245,158,11,0.15)] active:bg-amber-900/60'
            }`}
          >
            {(is_creator ? creator_ready : opponent_ready) ? 'Hazırım' : 'Hazır Ol'}
          </button>
        )}

        {is_creator && bothReady && (
          <button
            onClick={onStart}
            disabled={starting}
            className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 text-black font-bold
                       shadow-[0_4px_20px_rgba(245,158,11,0.25)] hover:shadow-[0_6px_28px_rgba(245,158,11,0.4)]
                       active:scale-[0.97] active:shadow-[0_2px_10px_rgba(245,158,11,0.2)] transition-all
                       disabled:opacity-60 disabled:cursor-not-allowed disabled:active:scale-100"
          >
            {starting ? 'Başlatılıyor…' : 'Düelloyu Başlat'}
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

function DuelloGame({ roomState, onAnswer, sounds }) {
  const [displayState, setDisplayState] = useState(roomState);
  const [localFeedback, setLocalFeedback] = useState(null);
  const [answerAnim, setAnswerAnim] = useState(null); // 'correct' | 'wrong' | null
  const feedbackUntil = useRef(0);
  const [selected, setSelected] = useState(null);
  const doubleChanceUsedRef = useRef(false);

  useEffect(() => {
    const now = Date.now();
    const serverQ = roomState?.current_question;
    const displayQ = displayState?.current_question;
    const advanced = serverQ !== displayQ || (roomState?.status === 'FINISHED' && displayState?.status !== 'FINISHED');
    const hasFeedback = displayState?.my_answer || localFeedback;

    if (advanced && hasFeedback && now < feedbackUntil.current) {
      const remaining = feedbackUntil.current - now;
      const timer = setTimeout(() => {
        setLocalFeedback(null);
        setDisplayState(roomState);
      }, remaining);
      return () => clearTimeout(timer);
    }

    setLocalFeedback(null);
    setDisplayState(roomState);

    // Çifte şans retry window'unda poll gelirse selected'ı sıfırla
    if (roomState?.my_answer && !roomState.my_answer.is_correct) {
      const jokers = roomState.player_jokers || {};
      const qIdx = roomState.current_question;
      if (jokers.double_chance === qIdx && !doubleChanceUsedRef.current) {
        setSelected(null);
        setAnswerAnim(null);
      }
    }
  }, [roomState]);

  const { question, opponent_answered, scores, current_question, total_questions, player_jokers, my_streak, room_id } = displayState || {};
  const my_answer = displayState?.my_answer || localFeedback;
  const [timeLeft, setTimeLeft] = useState(QUESTION_TIME);
  const [submitting, setSubmitting] = useState(false);
  const [eliminatedOptions, setEliminatedOptions] = useState([]);
  const [jokerLoading, setJokerLoading] = useState(false);
  const [posterHint, setPosterHint] = useState(null);
  const timerRef = useRef(null);
  const lastQIdx = useRef(-1);

  useEffect(() => {
    if (!question) return;
    if (question.index !== lastQIdx.current) {
      lastQIdx.current = question.index;
      setSelected(null);
      setSubmitting(false);
      setEliminatedOptions([]);
      setLocalFeedback(null);
      setAnswerAnim(null);
      setPosterHint(null);
      const serverRemaining = Math.ceil((question.time_remaining_ms || QUESTION_TIME * 1000) / 1000);
      setTimeLeft(Math.min(QUESTION_TIME, Math.max(0, serverRemaining)));
    }
  }, [question?.index]);

  useEffect(() => {
    if (my_answer || !question) return;
    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          return 0;
        }
        if (prev <= 6 && prev > 1) sounds?.playTick();
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [question?.index, my_answer]);

  useEffect(() => {
    if (question?.index !== undefined) doubleChanceUsedRef.current = false;
  }, [question?.index]);

  const handleSelect = async (option) => {
    const hasDoubleChance = player_jokers?.double_chance === question?.index && !doubleChanceUsedRef.current;
    const isDoubleRetry = !!(my_answer && !my_answer.is_correct && hasDoubleChance);

    if (submitting || timeLeft <= 0) return;
    if (isDoubleRetry) {
      // İkinci deneme: selected'ı sıfırla, eski seçimi yok say
    } else if (selected || my_answer) {
      return;
    }

    setSelected(option);
    setSubmitting(true);
    if (!isDoubleRetry) clearInterval(timerRef.current);
    try {
      const result = await onAnswer(question.index, option);
      if (result) {
        setLocalFeedback({
          selected: option,
          is_correct: result.is_correct,
          score: result.score,
          correct_answer: result.correct_answer,
        });
        if (result.is_correct) {
          sounds?.playCorrect();
          setAnswerAnim('correct');
        } else {
          sounds?.playWrong();
          setAnswerAnim('wrong');
        }

        if (isDoubleRetry) {
          // İkinci deneme bitti (doğru veya yanlış), artık kilitli
          doubleChanceUsedRef.current = true;
          feedbackUntil.current = Date.now() + 2000;
        } else if (hasDoubleChance && !result.is_correct) {
          // İlk deneme yanlış + çifte şans aktif → ikinci hak ver
          setTimeout(() => {
            setSelected(null);
            setAnswerAnim(null);
          }, 600);
        } else {
          // Normal cevap veya çifte şans olmadan
          feedbackUntil.current = Date.now() + 2000;
        }
      }
    } catch {
      setSelected(null);
    } finally {
      setSubmitting(false);
    }
  };

  const handleJoker = async (jokerType) => {
    if (jokerLoading || !question || timeLeft <= 0 || my_answer) return;
    setJokerLoading(true);
    try {
      const res = await callDuelloJoker(room_id, question.index, jokerType);
      sounds?.playJoker();
      if (jokerType === 'fifty_fifty' && res.eliminated) {
        setEliminatedOptions(res.eliminated);
      } else if (jokerType === 'freeze_time') {
        setTimeLeft(prev => prev + 10);
      } else if (jokerType === 'poster_hint') {
        setPosterHint(res.poster_url || 'not_found');
      }
    } catch (e) {
      console.error("Joker hatası:", e);
    } finally {
      setJokerLoading(false);
    }
  };

  if (!question) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-amber" size={32} />
      </div>
    );
  }

  const timerPct = (timeLeft / QUESTION_TIME) * 100;
  const timerColor = timeLeft > 10 ? 'text-green-400' : timeLeft > 5 ? 'text-yellow-400' : 'text-red-400';
  const movieName = question.extra_data?.movie;

  const urgentMode = timeLeft <= 5 && timeLeft > 0 && !my_answer;

  return (
    <div className="space-y-3 relative">
      {/* Son 5 saniye kenar glow'u */}
      <AnimatePresence>
        {urgentMode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.15, 0.35, 0.15] }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1, repeat: Infinity }}
            className="fixed inset-0 pointer-events-none z-50"
            style={{ boxShadow: 'inset 0 0 80px 20px rgba(239,68,68,0.25)' }}
          />
        )}
      </AnimatePresence>
      {/* Header: skor + süre + soru */}
      <div className="sticky top-0 z-10 -mx-4 px-4 pt-10 pb-3 bg-bg/95 backdrop-blur-sm border-b border-white/5">
        {/* Skorlar */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-xs text-fg-muted">Siz</span>
            <span className="text-lg font-bold text-amber tabular-nums">{scores?.me || 0}</span>
          </div>
          <div className="text-xs text-fg-subtle font-medium px-2 py-0.5 rounded-full bg-surface-2/40">
            {(current_question || 0) + 1} / {total_questions || TOTAL_QUESTIONS}
          </div>
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-lg font-bold text-fg tabular-nums">{scores?.opponent || 0}</span>
            <span className="text-xs text-fg-muted">Rakip</span>
          </div>
        </div>

        {/* Timer bar */}
        <div className={`relative h-1.5 bg-surface-2/50 rounded-full overflow-hidden ${
          timeLeft <= 5 && timeLeft > 0 && !my_answer ? 'animate-pulse' : ''
        }`}>
          <motion.div
            className={`absolute inset-y-0 left-0 rounded-full ${
              timeLeft > 10 ? 'bg-green-500' : timeLeft > 5 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            initial={false}
            animate={{
              width: `${timerPct}%`,
              ...(timeLeft <= 5 && timeLeft > 0 && !my_answer ? { opacity: [1, 0.6, 1] } : {}),
            }}
            transition={{
              width: { duration: 0.3 },
              opacity: { duration: 0.5, repeat: Infinity },
            }}
          />
        </div>

        {/* Timer sayacı + rakip durumu */}
        <div className="flex items-center justify-between mt-1.5">
          <motion.div
            className={`flex items-center gap-1 text-sm font-mono font-bold ${timerColor}`}
            animate={timeLeft <= 5 && timeLeft > 0 && !my_answer
              ? { scale: [1, 1.15, 1] }
              : { scale: 1 }
            }
            transition={{ duration: 0.5, repeat: timeLeft <= 5 && timeLeft > 0 ? Infinity : 0 }}
          >
            <Clock size={14} />
            {timeLeft}s
          </motion.div>
          {opponent_answered && !my_answer && (
            <motion.span
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-xs text-fg-subtle animate-pulse"
            >
              Rakip cevapladı!
            </motion.span>
          )}
        </div>
      </div>

      {/* Film referansı */}
      {movieName && my_answer && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center text-[10px] text-fg-subtle uppercase tracking-wider"
        >
          Film: {movieName}
        </motion.div>
      )}

      {/* Jokers & Streak */}
      <div className="flex items-center justify-between px-2">
        {/* Streak */}
        <div className="flex items-center gap-1.5">
          <Zap size={16} className={my_streak >= 2 ? "text-amber animate-pulse" : "text-amber/40"} />
          <span className={`text-xs font-bold ${my_streak >= 2 ? "text-amber" : "text-fg-subtle"}`}>
            Seri: {my_streak || 0} {my_streak >= 2 && <span className="text-amber/80 text-[10px] ml-1">(x1.5 Puan)</span>}
          </span>
        </div>

        {/* Jokerler */}
        <div className="flex items-center gap-1.5">
          {[
            { type: 'fifty_fifty', icon: Scissors, label: '%50', activeColor: 'border-amber/30 bg-amber/10 text-amber', hoverColor: 'hover:bg-amber/20' },
            { type: 'freeze_time', icon: Snowflake, label: '+10s', activeColor: 'border-blue-400/30 bg-blue-400/10 text-blue-400', hoverColor: 'hover:bg-blue-400/20' },
            { type: 'double_chance', icon: Dices, label: 'x2', activeColor: 'border-emerald/30 bg-emerald/10 text-emerald', hoverColor: 'hover:bg-emerald/20' },
            { type: 'poster_hint', icon: Image, label: '🖼️', activeColor: 'border-purple-400/30 bg-purple-400/10 text-purple-400', hoverColor: 'hover:bg-purple-400/20' },
          ].map(({ type, icon: Icon, label, activeColor, hoverColor }) => {
            const used = player_jokers?.[type] !== undefined;
            return (
              <button
                key={type}
                onClick={() => handleJoker(type)}
                disabled={my_answer || jokerLoading || timeLeft <= 0 || used}
                className={`relative px-2 py-1 rounded-lg border transition-all flex items-center gap-1 text-[11px] font-medium
                  ${used
                    ? 'border-fg-subtle/20 bg-surface-2/30 text-fg-subtle opacity-40'
                    : `${activeColor} ${hoverColor}`
                  } disabled:cursor-default`}
              >
                <Icon size={12} />
                <span>{label}</span>
                {used && (
                  <X size={16} className="absolute inset-0 m-auto text-red-400 opacity-80" strokeWidth={3} />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Soru metni */}
      <motion.p
        key={question.index}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="text-center text-fg font-medium text-sm sm:text-base leading-relaxed whitespace-pre-line"
      >
        {question.text}
      </motion.p>

      {/* Poster İpucu */}
      <AnimatePresence>
        {posterHint && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex justify-center"
          >
            {posterHint === 'not_found' ? (
              <div className="px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-400/30 text-purple-300 text-xs">
                Bu film için poster bulunamadı
              </div>
            ) : (
              <div className="relative w-20 h-28 rounded-lg overflow-hidden border border-purple-400/40 shadow-[0_0_15px_rgba(168,85,247,0.2)]">
                <img
                  src={posterHint}
                  alt="Film ipucu"
                  className="w-full h-full object-cover"
                  style={{ filter: 'blur(4px)' }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Seçenekler */}
      <div className="grid grid-cols-1 gap-2">
        {(question.options || []).map((option, i) => {
          const isDoubleChanceActive = my_answer && !my_answer.is_correct && player_jokers?.double_chance === question.index && !doubleChanceUsedRef.current;
          const correctAnswer = isDoubleChanceActive ? null : my_answer?.correct_answer;
          const isMyPick = my_answer && option === my_answer.selected;
          const isCorrectAnswer = my_answer && correctAnswer && option === correctAnswer;
          const isCorrect = isMyPick && my_answer.is_correct;
          const isWrong = isMyPick && !my_answer.is_correct;
          const isSelected = selected === option || isMyPick;

          const isEliminated = eliminatedOptions.includes(option);

          const isDisabled = (!!my_answer && !isDoubleChanceActive) || (!!selected && !isDoubleChanceActive) || timeLeft <= 0 || isEliminated || (isDoubleChanceActive && isMyPick);

          const shakeAnim = isWrong && answerAnim === 'wrong';
          const popAnim = isCorrect && answerAnim === 'correct';

          return (
            <motion.button
              key={`${question.index}-${i}`}
              initial={{ opacity: 0, x: -10 }}
              animate={
                shakeAnim
                  ? { opacity: 1, x: [0, -6, 6, -4, 4, 0] }
                  : popAnim
                    ? { opacity: 1, x: 0, scale: [1, 1.04, 1] }
                    : { opacity: 1, x: 0 }
              }
              transition={
                shakeAnim
                  ? { duration: 0.4 }
                  : popAnim
                    ? { duration: 0.3 }
                    : { duration: 0.2, delay: i * 0.05 }
              }
              onClick={() => handleSelect(option)}
              disabled={isDisabled}
              whileTap={!isDisabled ? { scale: 0.97 } : {}}
              className={`w-full px-4 py-3 rounded-xl border text-sm text-left transition-colors duration-200 ${
                isEliminated ? 'opacity-20 pointer-events-none' :
                isCorrect || (isCorrectAnswer && !isMyPick)
                  ? 'border-emerald bg-emerald text-emerald font-medium'
                  : isWrong
                    ? 'border-red-400 bg-rose text-red-400 font-medium'
                    : isSelected
                      ? 'border-amber bg-amber/20 text-fg'
                      : 'border-white/10 bg-surface-2/30 text-fg-muted hover:border-white/20 hover:bg-surface-2'
              } disabled:cursor-default`}
            >
              <div className="flex items-center justify-between">
                <span>{option}</span>
                {(isCorrect || (isCorrectAnswer && !isMyPick)) && <Check size={16} className="text-emerald" />}
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
          className={`text-center text-sm py-2 rounded-xl font-medium ${
            my_answer.is_correct ? 'text-emerald' : 'text-red-400'
          }`}
        >
          {my_answer.is_correct
            ? `Doğru! +${my_answer.score} puan`
            : 'Yanlış!'}
          {!opponent_answered && (
            <span className="block text-xs text-fg-subtle mt-1 font-normal">Rakip bekleniyor...</span>
          )}
        </motion.div>
      )}
    </div>
  );
}

// ─── TRANSITION: Son soru → Sonuç geçiş animasyonu ────────────────────────

function GameEndTransition({ scores, roomId, onComplete }) {
  const [prefetchedResults, setPrefetchedResults] = useState(null);
  const [minTimePassed, setMinTimePassed] = useState(false);
  const completedRef = useRef(false);

  useEffect(() => {
    getDuelloResults(roomId).then(setPrefetchedResults).catch(() => {});
  }, [roomId]);

  useEffect(() => {
    const t = setTimeout(() => setMinTimePassed(true), 2000);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    if (minTimePassed && prefetchedResults && !completedRef.current) {
      completedRef.current = true;
      onComplete(prefetchedResults);
    }
  }, [minTimePassed, prefetchedResults]);

  useEffect(() => {
    const fallback = setTimeout(() => {
      if (!completedRef.current) {
        completedRef.current = true;
        onComplete(prefetchedResults);
      }
    }, 4000);
    return () => clearTimeout(fallback);
  }, [prefetchedResults]);

  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-8">
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: 'spring', stiffness: 200, damping: 12, duration: 0.6 }}
      >
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-amber-500/20 to-amber-600/10 border-2 border-amber/30 flex items-center justify-center">
          <Trophy className="text-amber" size={48} />
        </div>
      </motion.div>

      <motion.h2
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.4 }}
        className="text-2xl font-bold text-amber tracking-wide"
      >
        Oyun Bitti!
      </motion.h2>

      {scores && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.4 }}
          className="flex items-center gap-6"
        >
          <div className="text-center">
            <div className="text-3xl font-bold text-amber">{scores.me || 0}</div>
            <div className="text-xs text-amber/50 mt-1">Sen</div>
          </div>
          <div className="text-amber/20 text-lg font-bold">–</div>
          <div className="text-center">
            <div className="text-3xl font-bold text-amber/60">{scores.opponent || 0}</div>
            <div className="text-xs text-amber/50 mt-1">Rakip</div>
          </div>
        </motion.div>
      )}

      <motion.div
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.3, duration: 0.8, ease: 'easeOut' }}
        className="w-48 h-px bg-gradient-to-r from-transparent via-amber/30 to-transparent"
      />
    </div>
  );
}

// ─── RESULTS: Oyun sonu ────────────────────────────────────────────────────

function DuelloResults({ roomId, prefetchedResults, onPlayAgain, onRematch, onGoHome }) {
  const [results, setResults] = useState(prefetchedResults || null);
  const [loading, setLoading] = useState(!prefetchedResults);
  const [rematchLoading, setRematchLoading] = useState(false);

  useEffect(() => {
    if (prefetchedResults) return;
    (async () => {
      try {
        const data = await getDuelloResults(roomId);
        setResults(data);
      } catch {}
      setLoading(false);
    })();
  }, [roomId, prefetchedResults]);

  if (loading || !results) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-amber" size={32} />
      </div>
    );
  }

  const { creator, opponent, winner_id, is_draw, questions } = results;
  const winner = winner_id === creator?.id ? creator : opponent;

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

      {/* ELO Değişimi */}
      {results.elo_changes && (() => {
        const ce = results.elo_changes.creator;
        const oe = results.elo_changes.opponent;
        return (
          <div className="flex items-center justify-center gap-6">
            <div className="flex flex-col items-center gap-0.5">
              <span className="text-[10px] text-amber/40">ELO</span>
              <span className="text-sm font-bold text-amber">{ce.after}</span>
              <span className={`text-xs font-bold ${ce.delta >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {ce.delta >= 0 ? `+${ce.delta}` : ce.delta}
              </span>
              {ce.league && <span className="text-[10px]">{ce.league.emoji} {ce.league.label}</span>}
            </div>
            <div className="text-amber/15 text-xs">|</div>
            <div className="flex flex-col items-center gap-0.5">
              <span className="text-[10px] text-amber/40">ELO</span>
              <span className="text-sm font-bold text-amber">{oe.after}</span>
              <span className={`text-xs font-bold ${oe.delta >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {oe.delta >= 0 ? `+${oe.delta}` : oe.delta}
              </span>
              {oe.league && <span className="text-[10px]">{oe.league.emoji} {oe.league.label}</span>}
            </div>
          </div>
        );
      })()}

      {/* Soru detayları */}
      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-amber/60 uppercase tracking-wider">Soru Detayları</h3>
        <div className="space-y-1.5 max-h-64 overflow-y-auto">
          {(questions || []).map((q, i) => {
            const ca = q.creator_answer;
            const oa = q.opponent_answer;
            return (
              <div key={i} className="bg-surface-2/30 border border-amber/10 rounded-xl px-3 py-2">
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
          onClick={async () => {
            if (rematchLoading) return;
            setRematchLoading(true);
            try {
              await onRematch(roomId);
            } catch {
              setRematchLoading(false);
            }
          }}
          disabled={rematchLoading}
          className="w-full py-3 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 text-black font-bold
                     hover:shadow-[0_0_20px_rgba(245,158,11,0.3)] transition-all flex items-center justify-center gap-2
                     disabled:opacity-60"
        >
          {rematchLoading ? <Loader2 size={16} className="animate-spin" /> : <RotateCcw size={16} />}
          {rematchLoading ? 'Oda kuruluyor...' : 'Rövanş!'}
        </button>
        <button
          onClick={onPlayAgain}
          className="w-full py-2.5 rounded-2xl border border-amber/20 text-amber/60 text-sm hover:bg-amber-900/10 transition-all"
        >
          Yeni Oyun (Farklı Kategori)
        </button>
        <button
          onClick={onGoHome}
          className="w-full py-2 rounded-2xl text-amber/40 text-xs hover:text-amber/60 transition-all"
        >
          Ana Sayfaya Dön
        </button>
      </div>
    </div>
  );
}

// ─── ANA SAYFA ─────────────────────────────────────────────────────────────

export default function QuizDuello() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const roomParam = searchParams.get('room');
  const sounds = useQuizSounds();

  useDocumentMeta({
    title: 'SineQuiz | Sinemood',
    description: 'Arkadaşınla 1v1 film bilgi yarışması! 10 soruda en iyi sinefil kim?',
  });

  const [phase, setPhase] = useState(roomParam ? 'lobby' : 'intro');
  const [roomId, setRoomId] = useState(roomParam || null);
  const [startingGame, setStartingGame] = useState(false);
  const [joinError, setJoinError] = useState('');
  const [prefetchedResults, setPrefetchedResults] = useState(null);

  const isPolling = phase === 'lobby' || phase === 'playing' || phase === 'transition';
  const { state: roomState, error: pollError, refetch } = useDuelloPoll(
    roomId, isPolling, phase === 'playing' ? 1500 : 2000
  );

  useEffect(() => {
    if (roomParam && phase === 'lobby' && !roomState) {
      (async () => {
        try {
          await joinDuelloRoom(roomParam);
        } catch (e) {
          if (!e.message?.includes('Kendi odana')) {
            setJoinError(e.message);
          }
        }
      })();
    }
  }, [roomParam]);

  useEffect(() => {
    if (!roomState) return;
    if (roomState.status === 'PLAYING' && phase !== 'playing') {
      setPhase('playing');
    } else if (roomState.status === 'FINISHED' && phase !== 'results' && phase !== 'transition') {
      if (phase === 'playing') {
        setPhase('transition');
      } else {
        setPhase('results');
      }
    } else if (roomState.status === 'ABANDONED') {
      setPhase('intro');
      setRoomId(null);
    }
  }, [roomState?.status]);

  const handleCreateRoom = (newRoomId) => {
    setRoomId(newRoomId);
    setPhase('lobby');
    window.history.replaceState({}, '', `/sinequiz?room=${newRoomId}`);
  };

  const handleJoinRoom = (code) => {
    setRoomId(code);
    setPhase('lobby');
    window.history.replaceState({}, '', `/sinequiz?room=${code}`);
  };

  const handleReady = async () => {
    sounds.warmUp();
    await setDuelloReady(roomId);
    refetch();
  };

  const handleStart = async () => {
    setStartingGame(true);
    try {
      await startDuello(roomId);
      refetch();
    } catch {
      setStartingGame(false);
    }
  };

  const handleLeave = async () => {
    await leaveDuelloRoom(roomId);
    setRoomId(null);
    setPhase('intro');
    window.history.replaceState({}, '', '/sinequiz');
  };

  const handleAnswer = async (questionIndex, answer) => {
    const result = await submitDuelloAnswer(roomId, questionIndex, answer);
    if (!result) throw new Error('submit failed');
    setTimeout(refetch, 300);
    return result;
  };

  const handlePlayAgain = () => {
    setRoomId(null);
    setPrefetchedResults(null);
    setPhase('intro');
    window.history.replaceState({}, '', '/sinequiz');
  };

  const handleRematch = async (oldRoomId) => {
    const data = await rematchDuello(oldRoomId);
    const newId = data.room_id;
    setRoomId(newId);
    setPrefetchedResults(null);
    setPhase('lobby');
    window.history.replaceState({}, '', `/sinequiz?room=${newId}`);
  };

  if (!isLoggedIn()) {
    return (
      <div className="min-h-screen bg-bg text-ivory">
        <div className="max-w-md mx-auto px-4 pt-20 text-center space-y-4">
          <Swords className="mx-auto text-amber/40" size={48} />
          <h2 className="text-lg font-bold text-amber">Giriş Gerekli</h2>
          <p className="text-sm text-fg-muted">SineQuiz oynamak için giriş yapmalısın.</p>
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
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
      className="min-h-screen bg-bg text-ivory pb-32"
    >
      <div className="max-w-md mx-auto px-4 pt-safe">
        {phase !== 'playing' && phase !== 'transition' && (
          <button
            onClick={() => phase === 'intro' ? navigate(-1) : handleLeave()}
            className="mt-3 mb-3 -ml-1 flex items-center gap-1.5 text-sm text-amber/50 hover:text-amber/80 active:text-amber/90 transition-colors group min-h-[44px] min-w-[44px] px-2"
          >
            <ChevronLeft size={20} className="group-hover:-translate-x-0.5 transition-transform" />
            {phase === 'intro' ? 'Geri' : 'Odadan Ayrıl'}
          </button>
        )}

        {joinError && (
          <div className="mb-4 p-3 rounded-xl bg-red-900/20 border border-red-500/30 text-red-400 text-xs text-center">
            {joinError}
          </div>
        )}

        {pollError && isPolling && (
          <div className="mb-4 p-3 rounded-xl bg-amber-900/20 border border-amber-500/30 text-amber-300/90 text-xs text-center"
               role="status">
            Bağlantı koptu, yeniden deneniyor… Oyun donmuş görünüyorsa internetini kontrol et.
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
              <DuelloIntro
                onCreateRoom={handleCreateRoom}
                onJoinRoom={handleJoinRoom}
                onNavigateLeaderboard={() => navigate('/sinequiz/skor-tablosu')}
              />
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
                roomId={roomId}
                roomState={roomState}
                onReady={handleReady}
                onStart={handleStart}
                starting={startingGame}
                onLeave={handleLeave}
              />
            </motion.div>
          )}

          {phase === 'playing' && roomState && (
            <motion.div
              key="playing"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <DuelloGame
                roomState={roomState}
                onAnswer={handleAnswer}
                sounds={sounds}
              />
            </motion.div>
          )}

          {phase === 'transition' && (
            <motion.div
              key="transition"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              transition={{ duration: 0.4 }}
            >
              <GameEndTransition
                scores={roomState?.scores}
                roomId={roomId}
                onComplete={(results) => {
                  setPrefetchedResults(results || null);
                  setPhase('results');
                }}
              />
            </motion.div>
          )}

          {phase === 'results' && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            >
              <DuelloResults
                roomId={roomId}
                prefetchedResults={prefetchedResults}
                onPlayAgain={handlePlayAgain}
                onRematch={handleRematch}
                onGoHome={() => navigate('/')}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
