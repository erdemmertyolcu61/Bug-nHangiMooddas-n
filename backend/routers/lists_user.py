"""
Kullanıcı İçeriği Router — Film puanı (1-10 + beğeni) ve Özel Listeler.

main.py'ye `app.include_router(user_content_router)` ile bağlanır.
Tüm rotalar `get_current_user` (JWT, type=='user') gerektirir — giriş zorunlu.
Editöryel `/api/lists` (Oscar/Cannes) DOKUNULMAZ; bunlar ayrı `/api/custom-lists`.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from backend.database import cache
from backend.routers.social import get_current_user
from backend.services.rate_limit import rate_limit_general

logger = logging.getLogger("user_content")

router = APIRouter(prefix="/api", tags=["user-content"], dependencies=[Depends(rate_limit_general)])


# ─── Request modelleri ───────────────────────────────────────────────────────
class RatingBody(BaseModel):
    reaction: Optional[str] = Field(default=None)  # 'like' | 'dislike' | None


class ListCreateBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)
    emoji: Optional[str] = Field(default=None, max_length=8)


class ListItemBody(BaseModel):
    tmdb_id: int = Field(..., ge=1)
    title: Optional[str] = Field(default=None, max_length=300)
    poster_url: Optional[str] = Field(default=None, max_length=500)


def _clean_reaction(reaction: Optional[str]) -> Optional[str]:
    return reaction if reaction in ("like", "dislike") else None


# ─── Film beğeni (like/dislike) ─────────────────────────────────────────────
@router.get("/movies/{movie_id}/rating")
async def get_movie_rating(movie_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    return await cache.get_rating(movie_id, user["user_id"])


@router.post("/movies/{movie_id}/rating")
async def save_movie_rating(body: RatingBody, movie_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    uid = user["user_id"]
    await cache.save_rating(movie_id, None, _clean_reaction(body.reaction), uid)
    try:
        await cache.invalidate_taste_profile(uid)
    except Exception:
        pass
    return {"status": "success", "reaction": _clean_reaction(body.reaction)}


# ─── Mood geri bildirim (bu film bu mood'a uyuyor mu?) ───────────────────────
class MoodFeedbackBody(BaseModel):
    mood_id: str = Field(..., min_length=2, max_length=30)
    feedback: str = Field(...)  # 'wrong_mood' | 'perfect_match'


@router.post("/movies/{movie_id}/mood-feedback")
async def save_mood_feedback(body: MoodFeedbackBody, movie_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    if body.feedback not in ("wrong_mood", "perfect_match"):
        raise HTTPException(status_code=422, detail="feedback must be 'wrong_mood' or 'perfect_match'")
    await cache.save_mood_feedback(user["user_id"], movie_id, body.mood_id, body.feedback)
    return {"status": "success"}


@router.get("/movies/{movie_id}/mood-feedback")
async def get_mood_feedback(movie_id: int = Path(..., ge=1), mood_id: str = "", user: dict = Depends(get_current_user)):
    if not mood_id:
        raise HTTPException(status_code=422, detail="mood_id query param required")
    my = await cache.get_mood_feedback(user["user_id"], movie_id, mood_id)
    stats = await cache.get_mood_feedback_stats(movie_id, mood_id)
    return {"my_feedback": my, "stats": stats}


# ─── Özel listeler ───────────────────────────────────────────────────────────
@router.get("/custom-lists")
async def list_custom_lists(user: dict = Depends(get_current_user)):
    return {"lists": await cache.get_lists(user["user_id"])}


@router.post("/custom-lists")
async def create_custom_list(body: ListCreateBody, user: dict = Depends(get_current_user)):
    list_id = await cache.create_list(user["user_id"], body.name.strip(), body.emoji)
    if not list_id:
        raise HTTPException(status_code=500, detail="Liste oluşturulamadı")
    return {"id": list_id, "name": body.name.strip(), "emoji": body.emoji, "count": 0, "covers": []}


@router.patch("/custom-lists/{list_id}")
async def rename_custom_list(body: ListCreateBody, list_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    ok = await cache.rename_list(list_id, user["user_id"], body.name.strip(), body.emoji)
    if not ok:
        raise HTTPException(status_code=404, detail="Liste bulunamadı")
    return {"status": "success"}


@router.delete("/custom-lists/{list_id}")
async def delete_custom_list(list_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    ok = await cache.delete_list(list_id, user["user_id"])
    if not ok:
        raise HTTPException(status_code=404, detail="Liste bulunamadı")
    return {"status": "success"}


@router.get("/custom-lists/{list_id}")
async def get_custom_list(list_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    data = await cache.get_list_items(list_id, user["user_id"])
    if data is None:
        raise HTTPException(status_code=404, detail="Liste bulunamadı")
    return data


@router.post("/custom-lists/{list_id}/items")
async def add_item_to_list(body: ListItemBody, list_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    ok = await cache.add_to_list(list_id, user["user_id"], body.tmdb_id, body.title or "", body.poster_url)
    if not ok:
        raise HTTPException(status_code=404, detail="Liste bulunamadı")
    return {"status": "success"}


@router.delete("/custom-lists/{list_id}/items/{tmdb_id}")
async def remove_item_from_list(list_id: int = Path(..., ge=1), tmdb_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    ok = await cache.remove_from_list(list_id, user["user_id"], tmdb_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Liste bulunamadı")
    return {"status": "success"}


# ─── Ortak liste (collaborator) ──────────────────────────────────────────────

class CollabInviteBody(BaseModel):
    username: str = Field(..., min_length=2, max_length=30)
    role: str = Field(default="editor")


class CollabRespondBody(BaseModel):
    accept: bool


@router.get("/custom-lists/{list_id}/collaborators")
async def list_collaborators(list_id: int = Path(..., ge=1), user: dict = Depends(get_current_user)):
    return {"collaborators": await cache.get_list_collaborators(list_id)}


@router.post("/custom-lists/{list_id}/collaborators")
async def invite_collaborator(body: CollabInviteBody, list_id: int = Path(..., ge=1),
                              user: dict = Depends(get_current_user)):
    from backend.database import _get_connection as _conn
    async with _conn(cache.db_path, user_data=True) as db:
        cur = await db.execute("SELECT id FROM users WHERE username = ?", (body.username,))
        target = await cur.fetchone()
    if not target:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    ok = await cache.invite_collaborator(list_id, user["user_id"], target[0], body.role)
    if not ok:
        raise HTTPException(400, "Davet gönderilemedi")

    # Push Notification: Katkıcı daveti bildirimi gönder (kendine gönderme)
    target_id = target[0]
    if target_id != user["user_id"]:
        try:
            from backend.services.push_service import send_push_to_user
            sender = await cache.get_user_by_username_by_id(user["user_id"])
            sender_name = (sender or {}).get("username") or (sender or {}).get("name") or "Bir arkadaşın"
            list_details = await cache.get_list_items(list_id, user["user_id"])
            list_name = list_details.get("name") if list_details else "bir liste"
            await send_push_to_user(
                target_id,
                "Sinemood",
                f"{sender_name} seni '{list_name}' listesine katkıcı olarak davet etti 🤝",
                url="/defterim?tab=lists", tag=f"collab-invite-{list_id}",
            )
        except Exception:
            pass

    return {"status": "success"}


@router.delete("/custom-lists/{list_id}/collaborators/{target_user_id}")
async def remove_collaborator_endpoint(list_id: int = Path(..., ge=1),
                                       target_user_id: int = Path(..., ge=1),
                                       user: dict = Depends(get_current_user)):
    ok = await cache.remove_collaborator(list_id, user["user_id"], target_user_id)
    if not ok:
        raise HTTPException(404, "İşlem yapılamadı")
    return {"status": "success"}


@router.get("/collab-invites")
async def get_collab_invites(user: dict = Depends(get_current_user)):
    return {"invites": await cache.get_collab_invites(user["user_id"])}


@router.post("/collab-invites/{list_id}/respond")
async def respond_collab_invite(body: CollabRespondBody, list_id: int = Path(..., ge=1),
                                user: dict = Depends(get_current_user)):
    ok = await cache.respond_collaboration(list_id, user["user_id"], body.accept)
    if not ok:
        raise HTTPException(404, "Davet bulunamadı")
    return {"status": "success"}


@router.get("/collaborated-lists")
async def get_collaborated_lists(user: dict = Depends(get_current_user)):
    return {"lists": await cache.get_collaborated_lists(user["user_id"])}


# ─── Herkese açık liste paylaşımı ────────────────────────────────────────────
import re as _re
import secrets as _secrets

from backend.database import _get_connection as _db_conn

_TR_MAP = str.maketrans("ğüşıöçĞÜŞİÖÇ", "gusiocGUSIOC")


def _slugify(name: str) -> str:
    s = name.translate(_TR_MAP).lower()
    s = _re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "liste"
    return f"{s}-{_secrets.token_hex(3)}"


class ListPublishBody(BaseModel):
    is_public: bool
    description: Optional[str] = Field(default=None, max_length=200)


@router.patch("/custom-lists/{list_id}/visibility")
async def set_list_visibility(body: ListPublishBody, list_id: int = Path(..., ge=1),
                              user: dict = Depends(get_current_user)):
    """Listeyi herkese açık yap / gizle. İlk açışta paylaşım slug'ı üretilir."""
    uid = user["user_id"]
    async with _db_conn(cache.db_path, user_data=True) as db:
        cur = await db.execute(
            "SELECT slug FROM user_lists WHERE id = ? AND user_id = ?", (list_id, uid)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(404, "Liste bulunamadı")
        slug = row[0]
        if body.is_public and not slug:
            cur = await db.execute(
                "SELECT name FROM user_lists WHERE id = ?", (list_id,)
            )
            name_row = await cur.fetchone()
            slug = _slugify((name_row[0] if name_row else "") or "liste")
        await db.execute(
            "UPDATE user_lists SET is_public = ?, slug = ?, description = ? WHERE id = ? AND user_id = ?",
            (int(body.is_public), slug, (body.description or "").strip() or None, list_id, uid),
        )
        await db.commit()
    return {"status": "success", "is_public": body.is_public, "slug": slug}


@router.get("/lists/public/{slug}")
async def get_public_list(slug: str = Path(..., max_length=60)):
    """Herkese açık liste — login gerektirmez (WhatsApp paylaşım hedefi)."""
    async with _db_conn(cache.db_path, user_data=True) as db:
        cur = await db.execute(
            """SELECT l.id, l.name, l.emoji, l.description, l.created_at,
                      u.id, u.username, u.name, u.picture
               FROM user_lists l JOIN users u ON u.id = l.user_id
               WHERE l.slug = ? AND l.is_public = 1""",
            (slug,),
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(404, "Liste bulunamadı ya da herkese açık değil")
        cur = await db.execute(
            """SELECT tmdb_id, title, poster_url, added_at FROM list_items
               WHERE list_id = ? ORDER BY added_at DESC LIMIT 100""",
            (row[0],),
        )
        items = await cur.fetchall()
    return {
        "name": row[1],
        "emoji": row[2] or "",
        "description": row[3] or "",
        "created_at": str(row[4] or ""),
        "owner": {"id": row[5], "username": row[6] or "", "name": row[7] or "", "avatar": row[8] or ""},
        "items": [
            {"tmdb_id": r[0], "title": r[1] or "", "poster_url": r[2] or "", "added_at": str(r[3] or "")}
            for r in items
        ],
        "count": len(items),
    }
