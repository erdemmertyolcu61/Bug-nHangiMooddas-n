/**
 * Global Arama Sayfası — /search?q=...
 * Ana sayfadan erişilir. Sonuçlar TMDB araması; bir filme tıklayınca
 * FilmDetailModal doğrudan açılır (Topluluğa Öner dahil).
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ChevronLeft, Search as SearchIcon, X, Users, RotateCcw, User, ChevronRight, Film } from 'lucide-react';
import { searchMovies, getPersonMovies, proxyImageUrl, recommendToCommunity, unrecommendFromCommunity, getCommunityRecommendations } from '../services/api';
import { getApiUrl, resolveAvatarUrl } from '../utils/apiConfig';
import { useAuth } from '../context/AuthContext';
import LottieAnimation from '../components/LottieAnimation';
import FilmDetailModal from '../components/FilmDetailModal';
import useDocumentMeta from '../utils/useDocumentMeta';

const IMG_BASE = 'https://image.tmdb.org/t/p/w500';

export default function SearchPage() {
  const navigate = useNavigate();
  useDocumentMeta({
    title: 'Film Ara | Sinemood',
    description: 'Binlerce film arasında ara, Üstad’ın notlarıyla keşfet.',
  });
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQ = searchParams.get('q') || '';

  const [query, setQuery] = useState(initialQ);
  const [results, setResults] = useState(null);
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedPerson, setExpandedPerson] = useState(null);
  const [personMovies, setPersonMovies] = useState([]);
  const [personMoviesLoading, setPersonMoviesLoading] = useState(false);
  const debounce = useRef(null);
  const inputRef = useRef(null);
  const abortRef = useRef(null);

  const [selectedMovie, setSelectedMovie] = useState(null);
  const [recommenders, setRecommenders] = useState([]);
  const [recommending, setRecommending] = useState(false);
  const { user } = useAuth();

  const runSearch = useCallback((q) => {
    clearTimeout(debounce.current);
    // Bayatlamış aramayı iptal et (her yeni sorgu öncekini durdurur)
    if (abortRef.current) abortRef.current.abort();
    if (!q.trim()) { setResults(null); setLoading(false); return; }
    setLoading(true);
    debounce.current = setTimeout(async () => {
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      try {
        const data = await searchMovies(q, { signal: ctrl.signal });
        setResults(data.movies || []);
        setPersons(data.persons || []);
        setExpandedPerson(null);
        setPersonMovies([]);
      } catch (e) {
        if (e?.name !== 'AbortError') { setResults([]); setPersons([]); }
      } finally {
        // Yalnızca hâlâ güncel istek isek loading'i kapat
        if (abortRef.current === ctrl) setLoading(false);
      }
    }, 400);
  }, []);

  // İlk yüklemede URL'deki q ile ara
  useEffect(() => {
    if (initialQ) runSearch(initialQ);
    inputRef.current?.focus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onChange = (e) => {
    const v = e.target.value;
    setQuery(v);
    setSearchParams(v.trim() ? { q: v } : {}, { replace: true });
    runSearch(v);
  };

  const clear = () => {
    setQuery('');
    setResults(null);
    setPersons([]);
    setExpandedPerson(null);
    setPersonMovies([]);
    setSearchParams({}, { replace: true });
    inputRef.current?.focus();
  };

  const togglePerson = async (person) => {
    if (expandedPerson?.id === person.id) {
      setExpandedPerson(null);
      setPersonMovies([]);
      return;
    }
    setExpandedPerson(person);
    setPersonMoviesLoading(true);
    try {
      const data = await getPersonMovies(person.id);
      setPersonMovies(data.movies || []);
    } catch {
      setPersonMovies([]);
    } finally {
      setPersonMoviesLoading(false);
    }
  };

  useEffect(() => {
    if (!selectedMovie?.id) { setRecommenders([]); return; }
    let active = true;
    setRecommenders([]);
    getCommunityRecommendations(selectedMovie.id).then((d) => {
      if (active) setRecommenders(d.recommenders || []);
    });
    return () => { active = false; };
  }, [selectedMovie?.id]);

  const alreadyRecommended = recommenders.some((r) => user && r.uid === user.id);

  const handleRecommendToCommunity = async () => {
    if (!selectedMovie || recommending) return;
    setRecommending(true);
    try {
      if (alreadyRecommended) {
        await unrecommendFromCommunity(selectedMovie.id);
        setRecommenders((prev) => prev.filter((r) => !(user && r.uid === user.id)));
      } else {
        const res = await recommendToCommunity(selectedMovie.id);
        setRecommenders((prev) => {
          const without = prev.filter((r) => r.uid !== res.shared_by.uid);
          return [res.shared_by, ...without];
        });
      }
    } catch (err) {
      console.error('Topluluk önerisi güncellenemedi:', err);
    } finally {
      setRecommending(false);
    }
  };

  const openMovie = async (m) => {
    setSelectedMovie({ id: m.id, title: m.title, poster_url: m.poster_url || (m.poster_path ? `${IMG_BASE}${m.poster_path}` : null), release_date: m.release_date, vote_average: m.vote_average, overview: m.overview });
    try {
      const res = await fetch(getApiUrl(`/api/movies/${m.id}/analyze`));
      if (res.ok) {
        const data = await res.json();
        setSelectedMovie((prev) => ({ ...prev, ...data }));
      }
    } catch {}
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
      className="min-h-screen bg-[#120d0b] text-ivory font-sans relative">
      <div className="fixed inset-0 pointer-events-none z-[999] opacity-[0.03] mix-blend-overlay"
           style={{ backgroundImage: "url('https://www.transparenttextures.com/patterns/natural-paper.png')" }} />

      <header className="sticky top-0 z-50 bg-[#120d0b]/98 border-b border-white/5 pt-safe">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-6 flex items-center gap-3 sm:gap-5">
          <button onClick={() => navigate(-1)}
            className="w-11 h-11 shrink-0 flex items-center justify-center hover:bg-white/5 rounded-full border border-white/10 transition-all">
            <ChevronLeft size={22} />
          </button>
          <div className="relative flex-1">
            <SearchIcon size={17} className="absolute left-4 top-1/2 -translate-y-1/2 text-ivory/25" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={onChange}
              placeholder="Film, oyuncu veya yönetmen ara..."
              aria-label="Film ara"
              className="w-full pl-11 pr-11 py-3.5 bg-white/5 border border-white/10 rounded-full text-[15px] text-ivory placeholder:text-ivory/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber/60 focus:border-amber/50 focus:bg-white/[0.07] transition-all"
            />
            {query && (
              <button onClick={clear}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-ivory/25 hover:text-ivory/60 transition-colors">
                <X size={17} />
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12 pb-nav">
        {/* Boş durum */}
        {results === null && !loading && (
          <div className="flex flex-col items-center justify-center text-center py-24 sm:py-32 gap-5">
            <LottieAnimation
              path="/lottie/search-empty.json"
              className="w-28 h-28"
              speed={0.7}
            />
            <div>
              <h2 className="font-serif text-2xl sm:text-3xl font-bold text-ivory mb-2">Ne aramıştın evlat?</h2>
              <p className="font-sans text-sm text-ivory/40 max-w-xs leading-relaxed">
                Aklındaki filmi yaz, Üstad'ın arşivinde bulalım.
              </p>
            </div>
          </div>
        )}

        {/* Yükleniyor */}
        {loading && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 sm:gap-6">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="aspect-[2/3] rounded-2xl bg-white/5 border border-white/10 animate-pulse" />
            ))}
          </div>
        )}

        {/* Sonuç yok */}
        {!loading && results !== null && results.length === 0 && persons.length === 0 && (
          <div className="flex flex-col items-center text-center py-24 sm:py-32 gap-4">
            <LottieAnimation
              path="/lottie/empty-state.json"
              className="w-24 h-24 opacity-60"
              speed={0.6}
            />
            <p className="font-serif text-xl sm:text-2xl italic text-ivory/40">
              &ldquo;{query}&rdquo; için bir şey bulamadım evlat.
            </p>
            <p className="font-sans text-sm text-ivory/25 mt-1">Başka bir isimle dene.</p>
          </div>
        )}

        {/* Kişi sonuçları */}
        {!loading && persons.length > 0 && (
          <div className="mb-8">
            <p className="font-sans text-[11px] font-bold uppercase tracking-[0.25em] text-ivory/30 mb-4">
              Kişiler
            </p>
            <div className="flex flex-col gap-3">
              {persons.map((p) => (
                <div key={p.id}>
                  <motion.button
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    onClick={() => togglePerson(p)}
                    className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl border transition-all duration-300 text-left ${expandedPerson?.id === p.id ? 'bg-amber/10 border-amber/30' : 'bg-white/[0.03] border-white/8 hover:bg-white/[0.06] hover:border-white/15'}`}
                  >
                    <div className="w-14 h-14 shrink-0 rounded-full overflow-hidden bg-white/5 border border-white/10">
                      {p.profile_path ? (
                        <img
                          src={proxyImageUrl(`${IMG_BASE}${p.profile_path}`)}
                          alt={p.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <span className="w-full h-full flex items-center justify-center">
                          <User size={22} className="text-ivory/20" />
                        </span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-sans text-[15px] font-semibold text-ivory/90">{p.name}</p>
                      <p className="font-sans text-[12px] text-ivory/35 mt-0.5">
                        {p.known_for_department === 'Acting' ? 'Oyuncu' : p.known_for_department === 'Directing' ? 'Yönetmen' : p.known_for_department || 'Sanatçı'}
                        {p.known_for?.length > 0 && (
                          <span className="text-ivory/25"> — {p.known_for.filter((k) => k.title).slice(0, 2).map((k) => k.title).join(', ')}</span>
                        )}
                      </p>
                    </div>
                    <ChevronRight size={18} className={`shrink-0 text-ivory/20 transition-transform duration-300 ${expandedPerson?.id === p.id ? 'rotate-90 text-amber' : ''}`} />
                  </motion.button>

                  {expandedPerson?.id === p.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="mt-3 ml-2 pl-4 border-l-2 border-amber/20"
                    >
                      {personMoviesLoading ? (
                        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
                          {[...Array(6)].map((_, i) => (
                            <div key={i} className="aspect-[2/3] rounded-xl bg-white/5 border border-white/10 animate-pulse" />
                          ))}
                        </div>
                      ) : personMovies.length > 0 ? (
                        <>
                          <p className="font-sans text-[11px] text-ivory/30 mb-3">
                            <Film size={12} className="inline mr-1.5 -mt-0.5" />
                            {personMovies.length} film
                          </p>
                          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
                            {personMovies.map((m, i) => (
                              <motion.button
                                key={m.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: Math.min(i * 0.02, 0.3) }}
                                onClick={() => openMovie(m)}
                                className="group text-left"
                                title={m.title}
                              >
                                <div className="aspect-[2/3] rounded-xl overflow-hidden bg-white/5 border border-white/10 group-hover:border-amber/40 transition-all duration-500 shadow-md">
                                  <img
                                    src={proxyImageUrl(m.poster_url || (m.poster_path ? `${IMG_BASE}${m.poster_path}` : null)) || 'https://via.placeholder.com/300x450'}
                                    alt={m.title}
                                    loading="lazy"
                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                                  />
                                </div>
                                <p className="mt-1.5 text-[11px] font-sans font-semibold text-ivory/60 group-hover:text-amber transition-colors line-clamp-2 leading-tight">
                                  {m.title}
                                </p>
                                {m.release_date && (
                                  <p className="text-[10px] text-ivory/20 font-sans mt-0.5">{m.release_date.split('-')[0]}</p>
                                )}
                              </motion.button>
                            ))}
                          </div>
                        </>
                      ) : (
                        <p className="text-[12px] text-ivory/30 py-4">Filmografi bulunamadı.</p>
                      )}
                    </motion.div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Film sonuçları */}
        {!loading && results !== null && results.length > 0 && (
          <>
            {persons.length > 0 && (
              <p className="font-sans text-[11px] font-bold uppercase tracking-[0.25em] text-ivory/30 mb-4 mt-2">
                Filmler
              </p>
            )}
            <p className="font-sans text-[11px] font-bold uppercase tracking-[0.25em] text-ivory/30 mb-6">
              {results.length} sonuç
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 sm:gap-6">
              {results.map((m, i) => (
                <motion.button
                  key={m.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: Math.min(i * 0.03, 0.4) }}
                  onClick={() => openMovie(m)}
                  className="group text-left"
                  title={m.title}
                >
                  <div className="aspect-[2/3] rounded-2xl overflow-hidden bg-white/5 border border-white/10 group-hover:border-amber/40 transition-all duration-500 shadow-lg">
                    <img
                      src={proxyImageUrl(m.poster_url || (m.poster_path ? `${IMG_BASE}${m.poster_path}` : null)) || 'https://via.placeholder.com/300x450'}
                      alt={m.title}
                      loading="lazy"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                    />
                  </div>
                  <p className="mt-2.5 text-[13px] font-sans font-semibold text-ivory/70 group-hover:text-amber transition-colors line-clamp-2 leading-tight">
                    {m.title}
                  </p>
                  {m.release_date && (
                    <p className="text-[11px] text-ivory/25 font-sans mt-0.5">{m.release_date.split('-')[0]}</p>
                  )}
                </motion.button>
              ))}
            </div>
          </>
        )}
      </main>

      {selectedMovie && (
        <FilmDetailModal
          movieId={selectedMovie.id || selectedMovie.tmdb_id}
          initialMovie={selectedMovie}
          onClose={() => setSelectedMovie(null)}
          headerBadge={recommenders.length > 0 ? (
            <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-slate-900/80 border border-white/5">
              <div className="flex -space-x-2">
                {recommenders.slice(0, 3).map((r) => (
                  <span key={r.uid} className="w-7 h-7 rounded-full overflow-hidden border-2 border-slate-900">
                    {r.avatar
                      ? <img src={resolveAvatarUrl(r.avatar)} alt="" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                      : <span className="w-full h-full flex items-center justify-center font-serif text-[11px] font-bold text-amber bg-slate-800">{r.username?.[0]}</span>}
                  </span>
                ))}
              </div>
              <p className="text-[11px] text-ivory/60">
                <span className="font-bold text-amber">Gurme {recommenders[0].username}</span>
                {recommenders.length > 1 && <span> ve {recommenders.length - 1} kişi daha</span>} önerdi
              </p>
            </div>
          ) : null}
          extraActions={user ? (
            <button onClick={handleRecommendToCommunity}
              disabled={recommending}
              title={alreadyRecommended ? 'Öneriyi geri al' : 'Topluluğa öner'}
              className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-all text-[11px] font-bold uppercase tracking-[0.12em] whitespace-nowrap ${alreadyRecommended ? 'bg-rose-500/15 border-rose-500/30 text-rose-300 hover:bg-rose-500/25' : 'bg-amber/12 border-amber/25 text-amber hover:bg-amber/25'}`}>
              {alreadyRecommended ? <><RotateCcw size={14} /> Öneriyi Geri Al</> : <><Users size={14} /> Topluluğa Öner</>}
            </button>
          ) : null}
        />
      )}
    </motion.div>
  );
}
