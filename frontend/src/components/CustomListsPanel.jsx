import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, ChevronLeft, ListPlus, X, Loader2, Globe2, Lock, Users, UserPlus, Check, XCircle } from 'lucide-react';
import {
  getCustomLists, createCustomList, deleteCustomList,
  getCustomList, removeFromCustomList, proxyImageUrl, setListVisibility,
  getListCollaborators, inviteCollaborator, removeCollaborator,
  getCollabInvites, respondCollabInvite, getCollaboratedLists,
  getFriends,
} from '../services/api';
import FilmDetailModal from './FilmDetailModal';
import ShareButtons from './ShareButtons';

const EMOJIS = ['🎬', '🍿', '🚀', '🌌', '🕵️', '💔', '😂', '👻', '🎭', '🏆', '🌙', '🔥'];

/**
 * Defterim "Listelerim" sekmesi — kullanıcının özel tematik listeleri.
 * Giriş zorunlu (backend). Anonim kullanıcıya giriş ipucu.
 */
export default function CustomListsPanel({ user }) {
  const [lists, setLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [newEmoji, setNewEmoji] = useState('🎬');
  const [busy, setBusy] = useState(false);

  const [openList, setOpenList] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailMovie, setDetailMovie] = useState(null);

  const [collabLists, setCollabLists] = useState([]);
  const [collabInvites, setCollabInvites] = useState([]);
  const [collabUsers, setCollabUsers] = useState([]);
  const [inviteUsername, setInviteUsername] = useState('');
  const [inviteBusy, setInviteBusy] = useState(false);
  const [showCollabPanel, setShowCollabPanel] = useState(false);
  const [friends, setFriends] = useState([]);
  const [friendsLoading, setFriendsLoading] = useState(false);

  const loadFriends = useCallback(async () => {
    if (!user) return;
    setFriendsLoading(true);
    try {
      const d = await getFriends();
      setFriends(d.friends || []);
    } catch {
      setFriends([]);
    } finally {
      setFriendsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (showCollabPanel) {
      loadFriends();
    }
  }, [showCollabPanel, loadFriends]);

  const loadLists = useCallback(async () => {
    setLoading(true);
    try {
      const [d, cl, inv] = await Promise.all([
        getCustomLists(),
        getCollaboratedLists().catch(() => ({ lists: [] })),
        getCollabInvites().catch(() => ({ invites: [] })),
      ]);
      setLists(d.lists || []);
      setCollabLists(cl.lists || []);
      setCollabInvites(inv.invites || []);
    } catch { setLists([]); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { if (user) loadLists(); else setLoading(false); }, [user, loadLists]);

  const handleCreate = async () => {
    const name = newName.trim();
    if (!name || busy) return;
    setBusy(true);
    try {
      await createCustomList(name, newEmoji);
      setNewName(''); setNewEmoji('🎬'); setCreating(false);
      await loadLists();
    } catch {} finally { setBusy(false); }
  };

  const handleDeleteList = async (id) => {
    setLists(prev => prev.filter(l => l.id !== id)); // optimistik
    try { await deleteCustomList(id); } catch { loadLists(); }
  };

  const openListDetail = async (list) => {
    setDetailLoading(true);
    setShowCollabPanel(false);
    setOpenList({ ...list, movies: [] });
    try {
      const [d, c] = await Promise.all([
        getCustomList(list.id),
        getListCollaborators(list.id).catch(() => ({ collaborators: [] })),
      ]);
      setOpenList(d);
      setCollabUsers(c.collaborators || []);
    } catch { setOpenList(null); }
    finally { setDetailLoading(false); }
  };

  const handleRemoveItem = async (tmdbId) => {
    if (!openList) return;
    setOpenList(prev => ({ ...prev, movies: prev.movies.filter(m => m.tmdb_id !== tmdbId) }));
    try { await removeFromCustomList(openList.id, tmdbId); } catch {}
    loadLists(); // sayım/kapak güncellensin
  };

  const handleRespondInvite = async (listId, accept) => {
    try {
      await respondCollabInvite(listId, accept);
      setCollabInvites(prev => prev.filter(i => i.list_id !== listId));
      if (accept) loadLists();
    } catch {}
  };

  const handleInviteCollab = async (username) => {
    const uname = (username || inviteUsername).trim();
    if (!uname || !openList || inviteBusy) return;
    setInviteBusy(true);
    try {
      await inviteCollaborator(openList.id, uname);
      setInviteUsername('');
      const c = await getListCollaborators(openList.id);
      setCollabUsers(c.collaborators || []);
    } catch {}
    finally { setInviteBusy(false); }
  };

  const handleRemoveCollab = async (targetUserId) => {
    if (!openList) return;
    try {
      await removeCollaborator(openList.id, targetUserId);
      setCollabUsers(prev => prev.filter(c => c.user_id !== targetUserId));
    } catch {}
  };

  const [visBusy, setVisBusy] = useState(false);
  const handleToggleVisibility = async () => {
    if (!openList || visBusy) return;
    setVisBusy(true);
    try {
      const next = !openList.is_public;
      const r = await setListVisibility(openList.id, next);
      setOpenList(prev => ({ ...prev, is_public: next, slug: r.slug || prev.slug }));
    } catch { /* sessiz */ }
    finally { setVisBusy(false); }
  };

  // ── Giriş yok ──
  if (!user) {
    return (
      <div className="p-8 sm:p-12 rounded-[2rem] bg-white/5 border border-white/10 text-center space-y-4">
        <ListPlus size={40} className="mx-auto text-amber/40" />
        <p className="font-serif text-lg italic text-ivory/60 max-w-md mx-auto">
          Kendi tematik listelerini ("Bilim kurgu maratonu", "Nolan filmleri") oluşturmak için giriş yap.
        </p>
      </div>
    );
  }

  // ── Liste detayı ──
  if (openList) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-between gap-4">
          <button onClick={() => setOpenList(null)}
            className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-ivory/50 hover:text-amber transition-all">
            <ChevronLeft size={16} /> Listelerim
          </button>
          <button onClick={() => { handleDeleteList(openList.id); setOpenList(null); }}
            className="flex items-center gap-2 px-4 py-2 rounded-full border border-rose-400/25 text-rose-300/80 text-[10px] font-bold uppercase tracking-wider hover:bg-rose-500/10 transition-all">
            <Trash2 size={13} /> Listeyi Sil
          </button>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-3xl">{openList.emoji || '🎬'}</span>
          <h2 className="text-2xl sm:text-4xl font-serif font-bold tracking-tight">{openList.name}</h2>
          <span className="text-sm text-ivory/40">{openList.movies?.length || 0} film</span>
        </div>

        {/* Herkese açık paylaşım ve katkıcılar paneli */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <div className="flex flex-wrap items-center gap-3">
            <button onClick={handleToggleVisibility} disabled={visBusy}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-full border text-[11px] font-bold uppercase tracking-wider transition-all cursor-pointer ${
                openList.is_public
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : 'bg-white/5 border-white/10 text-ivory/60 hover:border-amber/30'
              }`}>
              {visBusy ? <Loader2 size={13} className="animate-spin" />
                : openList.is_public ? <Globe2 size={13} /> : <Lock size={13} />}
              {openList.is_public ? 'Herkese Açık' : 'Gizli, paylaşmak için aç'}
            </button>
            {openList.is_public && openList.slug && (
              <div className="flex items-center">
                <ShareButtons
                  compact
                  url={`${window.location.origin}/liste/${openList.slug}`}
                  text={`${openList.emoji || '🎬'} "${openList.name}" listem Sinemood'da:`}
                />
              </div>
            )}
          </div>
          {openList.is_owner !== false && (
            <button onClick={() => setShowCollabPanel(p => !p)}
              className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-full border text-[11px] font-bold uppercase tracking-wider transition-all cursor-pointer w-full sm:w-auto ${
                showCollabPanel ? 'bg-indigo-500/15 border-indigo-400/40 text-indigo-300' : 'bg-white/5 border-white/10 text-ivory/60 hover:border-indigo-400/30'
              }`}>
              <Users size={13} /> Katkıcılar {collabUsers.filter(c => c.status === 'accepted').length > 0 && `(${collabUsers.filter(c => c.status === 'accepted').length})`}
            </button>
          )}
        </div>

        {/* Katkıcı yönetim paneli */}
        {showCollabPanel && openList.is_owner !== false && (
          <div className="p-4 rounded-2xl bg-indigo-500/[0.04] border border-indigo-400/20 space-y-3">
            <div className="flex flex-col sm:flex-row gap-2 relative">
              <div className="relative flex-1">
                <input value={inviteUsername} onChange={e => setInviteUsername(e.target.value.slice(0, 30))}
                  onKeyDown={e => e.key === 'Enter' && handleInviteCollab()}
                  placeholder="Arkadaşının kullanıcı adı"
                  className="w-full px-4 py-2.5 bg-ivory/5 border border-ivory/10 rounded-full text-sm text-ivory placeholder:text-ivory/30 focus:outline-none focus:border-indigo-400/40" />
                {inviteUsername.trim() && friends.filter(f =>
                  (f.username?.toLowerCase().includes(inviteUsername.toLowerCase()) ||
                   f.name?.toLowerCase().includes(inviteUsername.toLowerCase())) &&
                  !collabUsers.some(c => c.username === f.username || c.user_id === f.id)
                ).length > 0 && (
                  <div className="absolute left-0 right-0 mt-1 bg-bg border border-ivory/15 rounded-2xl shadow-xl max-h-48 overflow-y-auto z-50 divide-y divide-ivory/5">
                    {friends.filter(f =>
                      (f.username?.toLowerCase().includes(inviteUsername.toLowerCase()) ||
                       f.name?.toLowerCase().includes(inviteUsername.toLowerCase())) &&
                      !collabUsers.some(c => c.username === f.username || c.user_id === f.id)
                    ).map(f => (
                      <button key={f.id} onClick={() => handleInviteCollab(f.username)}
                        className="w-full px-4 py-2.5 text-left text-xs text-ivory/80 hover:bg-ivory/5 flex items-center gap-2 transition-colors first:rounded-t-2xl last:rounded-b-2xl cursor-pointer">
                        {f.avatar ? (
                          <img src={f.avatar} alt="" className="w-6 h-6 rounded-full object-cover shrink-0" />
                        ) : (
                          <div className="w-6 h-6 rounded-full bg-ivory/10 flex items-center justify-center text-[9px] font-bold text-ivory/60 shrink-0">{(f.username || '').slice(0, 2).toUpperCase()}</div>
                        )}
                        <div className="min-w-0 flex-1">
                          <p className="font-semibold text-ivory truncate">@{f.username}</p>
                          {f.name && <p className="text-[10px] text-ivory/40 truncate">{f.name}</p>}
                        </div>
                        <UserPlus size={12} className="text-indigo-400/60 shrink-0" />
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <button onClick={handleInviteCollab} disabled={inviteBusy || !inviteUsername.trim()}
                className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-full bg-indigo-500/15 border border-indigo-400/30 text-indigo-300 text-[11px] font-bold uppercase tracking-wider hover:bg-indigo-500/25 disabled:opacity-40 transition-all w-full sm:w-auto shrink-0 cursor-pointer">
                {inviteBusy ? <Loader2 size={13} className="animate-spin" /> : <><UserPlus size={13} /> Davet Et</>}
              </button>
            </div>
            {collabUsers.length > 0 && (
              <div className="space-y-2">
                {collabUsers.map(c => (
                  <div key={c.user_id} className="flex items-center justify-between gap-3 px-3 py-2 rounded-xl bg-ivory/[0.04]">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-sm font-medium text-ivory truncate">@{c.username || c.name}</span>
                      <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                        c.status === 'accepted' ? 'bg-emerald-500/15 text-emerald-400' :
                        c.status === 'pending' ? 'bg-amber/15 text-amber' : 'bg-white/5 text-ivory/40'
                      }`}>{c.status === 'accepted' ? 'Aktif' : c.status === 'pending' ? 'Bekliyor' : 'Reddetti'}</span>
                    </div>
                    <button onClick={() => handleRemoveCollab(c.user_id)}
                      className="text-ivory/30 hover:text-rose-300 transition-colors cursor-pointer">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
            {collabUsers.length === 0 && (
              <p className="text-[11px] text-ivory/40 italic">Henüz katkıcı yok. Arkadaşının kullanıcı adını yazıp davet et.</p>
            )}
          </div>
        )}

        {detailLoading ? (
          <div className="flex justify-center py-16"><Loader2 className="animate-spin text-amber/60" size={28} /></div>
        ) : (openList.movies || []).length === 0 ? (
          <p className="font-serif italic text-ivory/40 py-12 text-center">
            Bu liste boş. Bir filmin detayında "Listeye Ekle" ile film ekleyebilirsin.
          </p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 sm:gap-6">
            {openList.movies.map(m => (
              <motion.div key={m.tmdb_id} layout exit={{ opacity: 0, scale: 0.9 }}
                className="group relative rounded-2xl overflow-hidden bg-white/5 border border-white/8">
                <button onClick={() => setDetailMovie({ id: m.tmdb_id, title: m.title, poster_url: m.poster_url })}
                  className="block w-full aspect-[2/3]">
                  <img src={proxyImageUrl(m.poster_url) || 'https://via.placeholder.com/300x450'}
                    alt={m.title} loading="lazy" className="w-full h-full object-cover" />
                </button>
                <button onClick={() => handleRemoveItem(m.tmdb_id)} title="Listeden çıkar"
                  className="absolute top-2 right-2 w-8 h-8 flex items-center justify-center rounded-full bg-black/70 backdrop-blur text-ivory/80 hover:text-rose-300 opacity-0 group-hover:opacity-100 transition-all">
                  <X size={15} />
                </button>
                <p className="px-2 py-2 text-[11px] font-semibold text-ivory/80 line-clamp-1">{m.title}</p>
              </motion.div>
            ))}
          </div>
        )}

        {detailMovie && (
          <FilmDetailModal
            movieId={detailMovie.id}
            initialMovie={detailMovie}
            onClose={() => setDetailMovie(null)}
          />
        )}
      </div>
    );
  }

  // ── Liste listesi ──
  return (
    <div className="space-y-6">
      {/* Yeni liste oluştur */}
      <AnimatePresence mode="wait">
        {creating ? (
          <motion.div key="form" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="p-5 rounded-2xl bg-white/5 border border-amber/20 space-y-4">
            <div className="flex flex-wrap gap-1.5">
              {EMOJIS.map(e => (
                <button key={e} onClick={() => setNewEmoji(e)}
                  className={`w-9 h-9 rounded-full text-lg transition-all ${newEmoji === e ? 'bg-amber/20 border border-amber/40 scale-110' : 'bg-white/5 border border-white/10'}`}>
                  {e}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <input autoFocus value={newName} onChange={e => setNewName(e.target.value.slice(0, 60))}
                onKeyDown={e => e.key === 'Enter' && handleCreate()}
                placeholder="Liste adı (örn. Nolan filmleri)"
                className="flex-1 px-4 py-3 bg-black/30 border border-white/10 rounded-full text-base text-ivory placeholder:text-ivory/30 focus:outline-none focus:border-amber/40" />
              <button onClick={handleCreate} disabled={busy || !newName.trim()}
                className="w-10 h-10 flex items-center justify-center rounded-full bg-amber text-bg disabled:opacity-40 transition-all shrink-0">
                {busy ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
              </button>
              <button onClick={() => { setCreating(false); setNewName(''); }}
                className="w-10 h-10 flex items-center justify-center rounded-full bg-white/5 border border-white/10 text-ivory/50 hover:text-amber transition-all shrink-0">
                <X size={16} />
              </button>
            </div>
          </motion.div>
        ) : (
          <motion.button key="new" onClick={() => setCreating(true)}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex items-center gap-2 px-5 py-3 rounded-full bg-amber/10 border border-amber/30 text-amber text-[11px] font-bold uppercase tracking-wider hover:bg-amber/20 transition-all">
            <Plus size={15} /> Yeni Liste
          </motion.button>
        )}
      </AnimatePresence>

      {/* Bekleyen ortak liste davetleri */}
      {collabInvites.length > 0 && (
        <div className="space-y-2">
          {collabInvites.map(inv => (
            <div key={inv.list_id} className="flex items-center justify-between gap-3 p-4 rounded-2xl bg-amber/5 border border-amber/20">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-ivory">
                  <span className="text-amber">@{inv.owner_username}</span> seni
                  <span className="font-bold"> {inv.list_emoji} {inv.list_name}</span> listesine davet etti
                </p>
              </div>
              <div className="flex gap-2 shrink-0">
                <button onClick={() => handleRespondInvite(inv.list_id, true)}
                  className="w-8 h-8 flex items-center justify-center rounded-full bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-all">
                  <Check size={14} />
                </button>
                <button onClick={() => handleRespondInvite(inv.list_id, false)}
                  className="w-8 h-8 flex items-center justify-center rounded-full bg-rose-500/15 text-rose-400 hover:bg-rose-500/25 transition-all">
                  <XCircle size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Ortak olduğun listeler */}
      {collabLists.length > 0 && (
        <div className="space-y-3">
          <p className="text-[10px] font-bold uppercase tracking-widest text-ivory/40">Ortak Listeler</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
            {collabLists.map(list => (
              <motion.div key={`c-${list.id}`} layout
                className="group relative rounded-[1.75rem] overflow-hidden bg-white/5 border border-indigo-400/20 hover:border-indigo-400/40 transition-all">
                <button onClick={() => openListDetail(list)} className="block w-full text-left">
                  <div className="grid grid-cols-4 h-28 sm:h-32 bg-black/30">
                    {(list.covers && list.covers.length > 0 ? list.covers : [null, null, null, null]).slice(0, 4).map((c, i) => (
                      <div key={i} className="overflow-hidden">
                        {c ? <img src={proxyImageUrl(c)} alt="" className="w-full h-full object-cover" loading="lazy" />
                          : <div className="w-full h-full bg-white/[0.03]" />}
                      </div>
                    ))}
                  </div>
                  <div className="p-4 flex items-center gap-3">
                    <span className="text-2xl">{list.emoji || '🎬'}</span>
                    <div className="min-w-0 flex-1">
                      <p className="font-serif font-bold text-lg text-ivory truncate">{list.name}</p>
                      <p className="text-[11px] text-ivory/40">{list.count} film &middot; @{list.owner_username}</p>
                    </div>
                    <Users size={14} className="text-indigo-400/60 shrink-0" />
                  </div>
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-16"><Loader2 className="animate-spin text-amber/60" size={28} /></div>
      ) : lists.length === 0 ? (
        <p className="font-serif italic text-ivory/40 py-12 text-center">
          Henüz listen yok. "Yeni Liste" ile ilk tematik listeni oluştur.
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          {lists.map(list => (
            <motion.div key={list.id} layout
              className="group relative rounded-[1.75rem] overflow-hidden bg-white/5 border border-white/8 hover:border-amber/30 transition-all">
              <button onClick={() => openListDetail(list)} className="block w-full text-left">
                {/* Kapak kolajı */}
                <div className="grid grid-cols-4 h-28 sm:h-32 bg-black/30">
                  {(list.covers && list.covers.length > 0 ? list.covers : [null, null, null, null]).slice(0, 4).map((c, i) => (
                    <div key={i} className="overflow-hidden">
                      {c ? <img src={proxyImageUrl(c)} alt="" className="w-full h-full object-cover" loading="lazy" />
                        : <div className="w-full h-full bg-white/[0.03]" />}
                    </div>
                  ))}
                </div>
                <div className="p-4 flex items-center gap-3">
                  <span className="text-2xl">{list.emoji || '🎬'}</span>
                  <div className="min-w-0 flex-1">
                    <p className="font-serif font-bold text-lg text-ivory truncate">{list.name}</p>
                    <p className="text-[11px] text-ivory/40">{list.count} film</p>
                  </div>
                </div>
              </button>
              <button onClick={() => handleDeleteList(list.id)} title="Listeyi sil"
                className="absolute top-2 right-2 w-8 h-8 flex items-center justify-center rounded-full bg-black/70 backdrop-blur text-ivory/70 hover:text-rose-300 opacity-0 group-hover:opacity-100 transition-all">
                <Trash2 size={14} />
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
