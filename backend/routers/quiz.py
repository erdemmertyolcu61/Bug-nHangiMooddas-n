"""
Sinema Düello Router — Arkadaşla 1v1 film bilgi yarışması.

Oda sistemi (polling tabanlı), 7 farklı soru tipi, zamana dayalı puanlama.
main.py'ye `app.include_router(quiz_router)` ile bağlanır.
"""
import json
import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.auth_utils import verify_user, optional_user_id
from backend.database import cache, _get_connection as _db_conn
from backend.data.quiz_categories import QUIZ_CATEGORIES, MOOD_ID_LABELS

logger = logging.getLogger("quiz")

router = APIRouter(prefix="/api/game/quiz", tags=["quiz"])

QUESTIONS_PER_GAME = 10
QUESTION_TIME_MS = 30_000
ROOM_EXPIRE_MINUTES = 10


# ─── Pydantic Models ────────────────────────────────────────────────────────

class CreateRoomBody(BaseModel):
    categories: list[str] = Field(..., min_length=1, max_length=3)
    opponent_id: Optional[int] = None

class AnswerBody(BaseModel):
    question_index: int
    selected_answer: str

class JokerBody(BaseModel):
    question_index: int
    joker_type: str



# ─── Yardımcı Fonksiyonlar ───────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def _calculate_score(elapsed_ms: int) -> int:
    s = elapsed_ms / 1000.0
    if s <= 1.0:
        return 20
    if s >= 30.0:
        return 10
    return max(10, round(20 - (s - 1) * 10 / 29))


async def _user_info(user_id: int) -> dict:
    u = await cache.get_user_by_username_by_id(user_id)
    if not u:
        return {"id": user_id, "username": "?", "name": "?", "avatar": None}
    return {"id": u["id"], "username": u.get("username", ""),
            "name": u.get("name", ""), "avatar": u.get("picture")}


_ROOM_COLS = [
    "id", "creator_id", "opponent_id", "categories", "player_jokers", "status",
    "creator_ready", "opponent_ready", "current_question",
    "question_started_at", "winner_id", "created_at", "finished_at",
    "creator_elo_before", "opponent_elo_before", "creator_elo_after", "opponent_elo_after",
]

async def _get_room(db, room_id: str) -> dict:
    cur = await db.execute(
        f"SELECT {', '.join(_ROOM_COLS)} FROM quiz_rooms WHERE id = ?",
        (room_id,),
    )
    row = await cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Oda bulunamadı")
    return dict(zip(_ROOM_COLS, row))


async def _get_credits(tmdb_id: int) -> dict:
    """movie_credits_cache'den oku, yoksa TMDB'den çekip cache'le."""
    async with _db_conn(cache.db_path, user_data=True) as db:
        cur = await db.execute(
            "SELECT director, cast_json FROM movie_credits_cache WHERE tmdb_id = ?",
            (tmdb_id,),
        )
        row = await cur.fetchone()
        if row and row[0]:
            return {"director": row[0],
                    "cast": json.loads(row[1]) if row[1] else []}

    try:
        from backend.services.tmdb_service import tmdb_service
        data = await tmdb_service._get(
            f"{tmdb_service.base_url}/movie/{tmdb_id}/credits",
            {"api_key": tmdb_service.api_key},
        )
        cast_list = [
            {"name": a["name"], "character": a.get("character", "")}
            for a in data.get("cast", [])[:8]
        ]
        director = ""
        for crew in data.get("crew", []):
            if crew.get("job") == "Director":
                director = crew["name"]
                break

        async with _db_conn(cache.db_path, user_data=True) as db:
            await db.execute(
                """INSERT INTO movie_credits_cache (tmdb_id, director, cast_json)
                   VALUES (?, ?, ?)
                   ON CONFLICT(tmdb_id) DO UPDATE SET
                     director = excluded.director, cast_json = excluded.cast_json,
                     updated_at = CURRENT_TIMESTAMP""",
                (tmdb_id, director, json.dumps(cast_list, ensure_ascii=False)),
            )
            await db.commit()
        return {"director": director, "cast": cast_list}
    except Exception as e:
        logger.warning("[Quiz] Credits fetch failed for %s: %s", tmdb_id, e)
        return {"director": "", "cast": []}


# ─── Soru Üretim Motoru (Trivia tabanlı) ────────────────────────────────────

from backend.data.quiz_trivia import TRIVIA_QUESTIONS

async def _fetch_films_for_category(cat_slug: str, limit: int = 60) -> list:
    """Kategoriye göre movie_repository'den film çek."""
    cat = QUIZ_CATEGORIES.get(cat_slug)
    if not cat:
        return []

    qt = cat["query_type"]
    conn = cache._sync_conn()
    try:
        if qt == "mood":
            mood_ids = cat["mood_ids"]
            placeholders = ",".join("?" * len(mood_ids))
            rows = conn.execute(
                f"""SELECT DISTINCT tmdb_id, title, poster_url, overview, release_date,
                           vote_average, genre_ids, mood_id, original_language, mood_score
                    FROM movie_repository
                    WHERE mood_id IN ({placeholders})
                      AND poster_url IS NOT NULL AND poster_url != ''
                      AND vote_average >= 5.0
                    ORDER BY RANDOM() LIMIT ?""",
                mood_ids + [limit],
            ).fetchall()
        elif qt == "genre":
            genre_ids = cat["genre_ids"]
            like_clauses = " OR ".join(f"genre_ids LIKE '%{gid}%'" for gid in genre_ids)
            rows = conn.execute(
                f"""SELECT DISTINCT tmdb_id, title, poster_url, overview, release_date,
                           vote_average, genre_ids, mood_id, original_language, mood_score
                    FROM movie_repository
                    WHERE ({like_clauses})
                      AND poster_url IS NOT NULL AND poster_url != ''
                      AND vote_average >= 5.0
                    ORDER BY RANDOM() LIMIT ?""",
                (limit,),
            ).fetchall()
        elif qt == "language":
            lang = cat["original_language"]
            rows = conn.execute(
                """SELECT DISTINCT tmdb_id, title, poster_url, overview, release_date,
                          vote_average, genre_ids, mood_id, original_language, mood_score
                   FROM movie_repository
                   WHERE original_language = ?
                     AND poster_url IS NOT NULL AND poster_url != ''
                     AND vote_average >= 4.0
                   ORDER BY RANDOM() LIMIT ?""",
                (lang, limit),
            ).fetchall()
        elif qt == "year_range":
            year_min = cat.get("year_min", 1900)
            year_max = cat.get("year_max", 2099)
            rows = conn.execute(
                """SELECT DISTINCT tmdb_id, title, poster_url, overview, release_date,
                          vote_average, genre_ids, mood_id, original_language, mood_score
                   FROM movie_repository
                   WHERE CAST(SUBSTR(release_date,1,4) AS INTEGER) >= ?
                     AND CAST(SUBSTR(release_date,1,4) AS INTEGER) <= ?
                     AND poster_url IS NOT NULL AND poster_url != ''
                     AND vote_average >= 5.0
                   ORDER BY RANDOM() LIMIT ?""",
                (year_min, year_max, limit),
            ).fetchall()
        elif qt == "min_rating":
            min_avg = cat.get("min_vote_average", 7.0)
            min_cnt = cat.get("min_vote_count", 100)
            rows = conn.execute(
                """SELECT DISTINCT tmdb_id, title, poster_url, overview, release_date,
                          vote_average, genre_ids, mood_id, original_language, mood_score
                   FROM movie_repository
                   WHERE vote_average >= ?
                     AND vote_count >= ?
                     AND poster_url IS NOT NULL AND poster_url != ''
                   ORDER BY RANDOM() LIMIT ?""",
                (min_avg, min_cnt, limit),
            ).fetchall()
        else:
            rows = []
    finally:
        conn.close()

    return [
        {
            "tmdb_id": r[0], "title": r[1], "poster_url": r[2],
            "overview": r[3], "release_date": r[4], "vote_average": r[5],
            "genre_ids": r[6], "mood_id": r[7], "original_language": r[8],
            "mood_score": r[9],
        }
        for r in rows
    ]


def _generate_questions_from_trivia(categories: list[str]) -> list[dict]:
    """Trivia veritabanından 10 soru seç: ilk 3 kategoriden 3'er, 4. kategoriden 1."""
    by_cat: dict[str, list] = {}
    for q in TRIVIA_QUESTIONS:
        by_cat.setdefault(q["category"], []).append(q)

    distribution = [(cat, 3) for cat in categories[:3]]
    if len(categories) > 3:
        distribution.append((categories[3], 1))

    questions = []
    used_indices = set()

    for cat_slug, count in distribution:
        pool = by_cat.get(cat_slug, [])
        if not pool:
            continue
        random.shuffle(pool)
        added = 0
        for trivia in pool:
            if added >= count:
                break
            idx = id(trivia)
            if idx in used_indices:
                continue
            used_indices.add(idx)

            options = [trivia["correct"]] + trivia["wrong"][:3]
            random.shuffle(options)

            questions.append({
                "question_type": "trivia",
                "category_slug": cat_slug,
                "tmdb_id": 0,
                "question_text": trivia["question"],
                "correct_answer": trivia["correct"],
                "options": json.dumps(options, ensure_ascii=False),
                "hint_image": None,
                "extra_data": json.dumps({"movie": trivia.get("movie", "")}, ensure_ascii=False),
            })
            added += 1

    while len(questions) < QUESTIONS_PER_GAME:
        pool = [t for t in TRIVIA_QUESTIONS if id(t) not in used_indices and t["category"] in categories]
        if not pool:
            pool = [t for t in TRIVIA_QUESTIONS if t["category"] in categories]
            used_indices -= {id(t) for t in pool}
        if not pool:
            pool = [t for t in TRIVIA_QUESTIONS if id(t) not in used_indices]
        if not pool:
            break
        trivia = random.choice(pool)
        used_indices.add(id(trivia))
        options = [trivia["correct"]] + trivia["wrong"][:3]
        random.shuffle(options)
        questions.append({
            "question_type": "trivia",
            "category_slug": trivia["category"],
            "tmdb_id": 0,
            "question_text": trivia["question"],
            "correct_answer": trivia["correct"],
            "options": json.dumps(options, ensure_ascii=False),
            "hint_image": None,
            "extra_data": json.dumps({"movie": trivia.get("movie", "")}, ensure_ascii=False),
        })

    random.shuffle(questions)

    for i, q in enumerate(questions):
        q["question_index"] = i

    return questions[:QUESTIONS_PER_GAME]


# ─── Soru İlerleme / Timer Yönetimi ─────────────────────────────────────────

async def _check_advance_question(db, room: dict) -> dict:
    """Soru ilerleme kontrolü: ikisi de cevapladıysa veya süre dolduysa ilerle."""
    if room["status"] != "PLAYING" or room["current_question"] < 0:
        return room

    q_idx = room["current_question"]
    started_at = room.get("question_started_at")

    if not started_at:
        return room

    started_ms = int(datetime.fromisoformat(started_at).timestamp() * 1000)
    now_ms = _now_ms()
    elapsed = now_ms - started_ms
    time_expired = elapsed >= QUESTION_TIME_MS + 2000

    cur = await db.execute(
        "SELECT COUNT(*) FROM quiz_answers WHERE room_id = ? AND question_index = ?",
        (room["id"], q_idx),
    )
    answer_count = (await cur.fetchone())[0]
    both_answered = answer_count >= 2

    if not both_answered and not time_expired:
        return room

    next_q = q_idx + 1
    if next_q >= QUESTIONS_PER_GAME:
        winner_id = await _compute_winner(db, room["id"], room["creator_id"], room["opponent_id"])
        res = await db.execute(
            """UPDATE quiz_rooms SET status = 'FINISHED', current_question = ?,
               winner_id = ?, finished_at = CURRENT_TIMESTAMP
               WHERE id = ? AND current_question = ?""",
            (q_idx, winner_id, room["id"], q_idx),
        )
        await db.commit()
        if res.rowcount == 0:
            return await _get_room(db, room["id"])
        await _update_stats(db, room["id"], room["creator_id"], room["opponent_id"], winner_id)
        room["status"] = "FINISHED"
        room["winner_id"] = winner_id
    else:
        new_started = _now_iso()
        res = await db.execute(
            """UPDATE quiz_rooms SET current_question = ?, question_started_at = ?
               WHERE id = ? AND current_question = ?""",
            (next_q, new_started, room["id"], q_idx),
        )
        await db.commit()
        if res.rowcount == 0:
            return await _get_room(db, room["id"])
        room["current_question"] = next_q
        room["question_started_at"] = new_started

    return room


def _get_league(elo: int) -> dict:
    if elo >= 1800:
        return {"tier": "sine-guru", "label": "Sine-Guru", "emoji": "💎"}
    if elo >= 1500:
        return {"tier": "altin", "label": "Altın", "emoji": "🥇"}
    if elo >= 1200:
        return {"tier": "gumus", "label": "Gümüş", "emoji": "🥈"}
    return {"tier": "bronz", "label": "Bronz", "emoji": "🥉"}


def _compute_elo_change(rating_a: int, rating_b: int, score_a: float, games_a: int) -> int:
    k = 32 if games_a < 30 else 24
    expected = 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))
    return round(k * (score_a - expected))


async def _get_elo(db, user_id: int) -> tuple[int, int]:
    cur = await db.execute(
        "SELECT elo_rating, games_played FROM quiz_stats WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    if row:
        return (row[0] or 1000, row[1] or 0)
    return (1000, 0)


async def _update_elo(db, room_id: str, creator_id: int, opponent_id: int, winner_id: Optional[int]):
    creator_elo, creator_games = await _get_elo(db, creator_id)
    opponent_elo, opponent_games = await _get_elo(db, opponent_id)

    if winner_id is None:
        c_score, o_score = 0.5, 0.5
    elif winner_id == creator_id:
        c_score, o_score = 1.0, 0.0
    else:
        c_score, o_score = 0.0, 1.0

    c_delta = _compute_elo_change(creator_elo, opponent_elo, c_score, creator_games)
    o_delta = _compute_elo_change(opponent_elo, creator_elo, o_score, opponent_games)

    new_c = max(100, creator_elo + c_delta)
    new_o = max(100, opponent_elo + o_delta)

    for uid, new_elo in ((creator_id, new_c), (opponent_id, new_o)):
        await db.execute(
            "UPDATE quiz_stats SET elo_rating = ?, elo_peak = MAX(COALESCE(elo_peak, 1000), ?) WHERE user_id = ?",
            (new_elo, new_elo, uid),
        )

    await db.execute(
        """UPDATE quiz_rooms SET creator_elo_before = ?, opponent_elo_before = ?,
           creator_elo_after = ?, opponent_elo_after = ? WHERE id = ?""",
        (creator_elo, opponent_elo, new_c, new_o, room_id),
    )


async def _compute_winner(db, room_id: str, creator_id: int, opponent_id: int) -> Optional[int]:
    cur = await db.execute(
        """SELECT user_id, SUM(score) as total_score,
                  SUM(is_correct) as total_correct,
                  SUM(elapsed_ms) as total_time
           FROM quiz_answers WHERE room_id = ?
           GROUP BY user_id""",
        (room_id,),
    )
    rows = await cur.fetchall()
    if not rows:
        return None

    scores = {}
    for r in rows:
        scores[r[0]] = {"score": r[1] or 0, "correct": r[2] or 0, "time": r[3] or 0}

    p1 = scores.get(creator_id, {"score": 0, "correct": 0, "time": 999999})
    p2 = scores.get(opponent_id, {"score": 0, "correct": 0, "time": 999999})

    if p1["score"] != p2["score"]:
        return creator_id if p1["score"] > p2["score"] else opponent_id
    if p1["correct"] != p2["correct"]:
        return creator_id if p1["correct"] > p2["correct"] else opponent_id
    if p1["time"] != p2["time"]:
        return creator_id if p1["time"] < p2["time"] else opponent_id
    return None


async def _update_stats(db, room_id: str, creator_id: int, opponent_id: int, winner_id: Optional[int]):
    cur = await db.execute(
        "SELECT user_id, SUM(score) FROM quiz_answers WHERE room_id = ? GROUP BY user_id",
        (room_id,),
    )
    score_rows = await cur.fetchall()
    game_scores = {r[0]: r[1] or 0 for r in score_rows}

    for uid in (creator_id, opponent_id):
        won = 1 if uid == winner_id else 0
        game_score = game_scores.get(uid, 0)

        cur2 = await db.execute(
            "SELECT user_id, games_played, games_won, total_score, best_score, win_streak, best_streak FROM quiz_stats WHERE user_id = ?",
            (uid,),
        )
        existing = await cur2.fetchone()

        if existing:
            _sc = ["user_id", "games_played", "games_won", "total_score", "best_score", "win_streak", "best_streak"]
            stats = dict(zip(_sc, existing))
            new_played = stats["games_played"] + 1
            new_won = stats["games_won"] + won
            new_total = stats["total_score"] + game_score
            new_best = max(stats["best_score"], game_score)
            new_streak = (stats["win_streak"] + 1) if won else 0
            new_best_streak = max(stats["best_streak"], new_streak)
            await db.execute(
                """UPDATE quiz_stats SET games_played=?, games_won=?, total_score=?,
                   best_score=?, win_streak=?, best_streak=?, updated_at=CURRENT_TIMESTAMP
                   WHERE user_id=?""",
                (new_played, new_won, new_total, new_best, new_streak, new_best_streak, uid),
            )
        else:
            await db.execute(
                """INSERT INTO quiz_stats (user_id, games_played, games_won, total_score,
                   best_score, win_streak, best_streak, elo_rating, elo_peak)
                   VALUES (?, 1, ?, ?, ?, ?, ?, 1000, 1000)""",
                (uid, won, game_score, game_score, 1 if won else 0, 1 if won else 0),
            )

    await _update_elo(db, room_id, creator_id, opponent_id, winner_id)
    await db.commit()


# ─── Endpoint'ler ────────────────────────────────────────────────────────────

@router.get("/categories")
async def list_categories():
    """Seçilebilir kategori listesi."""
    result = []
    for slug, cat in QUIZ_CATEGORIES.items():
        result.append({
            "slug": slug,
            "label": cat["label"],
            "emoji": cat["emoji"],
        })
    return {"categories": result}


@router.post("/rooms")
async def create_room(body: CreateRoomBody, user: dict = Depends(verify_user)):
    """Oda oluştur. 3 kategori seç, 1 rastgele eklenir. Oda kodu döner."""
    me = user["user_id"]
    opponent_id = body.opponent_id

    if opponent_id and opponent_id == me:
        raise HTTPException(status_code=400, detail="Kendinle oynayamazsın")

    for cat in body.categories:
        if cat != "rastgele" and cat not in QUIZ_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Geçersiz kategori: {cat}")

    all_cats = list(body.categories)
    if "rastgele" in all_cats:
        all_cats.remove("rastgele")
        remaining = [k for k in QUIZ_CATEGORIES if k not in all_cats]
        if remaining:
            all_cats.append(random.choice(remaining))

    room_id = uuid.uuid4().hex[:6].upper()

    try:
        async with _db_conn(cache.db_path, user_data=True) as db:
            await db.execute(
                """INSERT INTO quiz_rooms (id, creator_id, opponent_id, categories, status)
                   VALUES (?, ?, ?, ?, 'WAITING')""",
                (room_id, me, opponent_id, json.dumps(all_cats)),
            )
            await db.commit()
    except Exception as e:
        logger.exception("create_room DB error for user=%s: %s", me, e)
        raise HTTPException(status_code=500, detail=f"Oda oluşturulurken hata: {e}")

    if opponent_id:
        try:
            from backend.services.push_service import send_push_to_user
            sender = await cache.get_user_by_username_by_id(me)
            sender_name = (sender or {}).get("username") or (sender or {}).get("name") or "Biri"
            await send_push_to_user(
                opponent_id,
                "SineQuiz",
                f"{sender_name} seni SineQuiz'e davet ediyor! Oda kodu: {room_id}",
                url=f"/sinequiz?room={room_id}",
                tag=f"quiz-invite-{room_id}",
            )
        except Exception:
            pass

    return {
        "room_id": room_id,
        "categories": all_cats,
        "status": "WAITING",
    }


@router.get("/rooms/{room_id}")
async def poll_room(room_id: str, user: dict = Depends(verify_user)):
    """Oda durumunu poll et. Oyun sırasında 2.5s aralıkla çağrılır."""
    me = user["user_id"]

    try:
        async with _db_conn(cache.db_path, user_data=True) as db:
            room = await _get_room(db, room_id)

            if me != room["creator_id"] and me != room.get("opponent_id"):
                raise HTTPException(status_code=403, detail="Bu odada değilsin")

            if room["status"] == "PLAYING":
                room = await _check_advance_question(db, room)

            is_creator = me == room["creator_id"]
            categories = json.loads(room["categories"]) if isinstance(room["categories"], str) else room["categories"]

            cat_labels = []
            for cs in categories:
                cat_def = QUIZ_CATEGORIES.get(cs)
                cat_labels.append({
                    "slug": cs,
                    "label": cat_def["label"] if cat_def else cs,
                    "emoji": cat_def["emoji"] if cat_def else "",
                })

            creator_elo, _ = await _get_elo(db, room["creator_id"])
            creator_info = {**(await _user_info(room["creator_id"])),
                            "elo_rating": creator_elo, "league": _get_league(creator_elo)}
            opponent_info = None
            if room["opponent_id"]:
                opp_elo, _ = await _get_elo(db, room["opponent_id"])
                opponent_info = {**(await _user_info(room["opponent_id"])),
                                 "elo_rating": opp_elo, "league": _get_league(opp_elo)}

            response = {
                "room_id": room_id,
                "status": room["status"],
                "creator": creator_info,
                "opponent": opponent_info,
                "creator_ready": bool(room["creator_ready"]),
                "opponent_ready": bool(room["opponent_ready"]),
                "categories": cat_labels,
                "is_creator": is_creator,
            }

            if room["status"] == "PLAYING":
                q_idx = room["current_question"]
                cur = await db.execute(
                    """SELECT question_type, question_text, options, hint_image, extra_data
                       FROM quiz_questions WHERE room_id = ? AND question_index = ?""",
                    (room_id, q_idx),
                )
                q_row = await cur.fetchone()

                started_at = room.get("question_started_at", "")
                time_remaining = QUESTION_TIME_MS
                if started_at:
                    started_ms = int(datetime.fromisoformat(started_at).timestamp() * 1000)
                    time_remaining = max(0, QUESTION_TIME_MS - (_now_ms() - started_ms))

                question_data = None
                if q_row:
                    question_data = {
                        "index": q_idx,
                        "type": q_row[0],
                        "text": q_row[1],
                        "options": json.loads(q_row[2]),
                        "hint_image": q_row[3],
                        "extra_data": json.loads(q_row[4]) if q_row[4] else None,
                        "time_remaining_ms": time_remaining,
                    }

                cur_ans = await db.execute(
                    "SELECT selected_answer, is_correct, score FROM quiz_answers WHERE room_id = ? AND question_index = ? AND user_id = ?",
                    (room_id, q_idx, me),
                )
                my_ans_row = await cur_ans.fetchone()
                my_answer = None
                if my_ans_row:
                    my_answer = {
                        "selected": my_ans_row[0],
                        "is_correct": bool(my_ans_row[1]),
                        "score": my_ans_row[2],
                    }

                opponent_id = room["opponent_id"] if is_creator else room["creator_id"]
                cur_opp = await db.execute(
                    "SELECT COUNT(*) FROM quiz_answers WHERE room_id = ? AND question_index = ? AND user_id = ?",
                    (room_id, q_idx, opponent_id),
                )
                opp_answered = (await cur_opp.fetchone())[0] > 0

                cur_scores = await db.execute(
                    "SELECT user_id, SUM(score) FROM quiz_answers WHERE room_id = ? GROUP BY user_id",
                    (room_id,),
                )
                score_rows = await cur_scores.fetchall()
                score_map = {r[0]: r[1] or 0 for r in score_rows}

                cur_streak = await db.execute("SELECT is_correct FROM quiz_answers WHERE room_id = ? AND user_id = ? ORDER BY question_index ASC", (room_id, me))
                streak_rows = await cur_streak.fetchall()
                my_streak = 0
                for r in streak_rows:
                    if r[0]: my_streak += 1
                    else: my_streak = 0
                    
                jokers_dict = json.loads(room.get("player_jokers") or "{}")
                my_jokers = jokers_dict.get(str(me), {})

                if my_ans_row and my_answer:
                    has_dc = my_jokers.get("double_chance") == q_idx
                    is_wrong = not my_answer["is_correct"]
                    dc_retry_window = has_dc and is_wrong
                    if not dc_retry_window:
                        cur_correct = await db.execute(
                            "SELECT correct_answer FROM quiz_questions WHERE room_id = ? AND question_index = ?",
                            (room_id, q_idx),
                        )
                        correct_row = await cur_correct.fetchone()
                        if correct_row:
                            my_answer["correct_answer"] = correct_row[0]

                response.update({
                    "current_question": q_idx,
                    "total_questions": QUESTIONS_PER_GAME,
                    "question": question_data,
                    "my_answer": my_answer,
                    "my_streak": my_streak,
                    "player_jokers": my_jokers,
                    "opponent_answered": opp_answered,
                    "scores": {
                        "me": score_map.get(me, 0),
                        "opponent": score_map.get(opponent_id, 0),
                    },
                })

            elif room["status"] == "FINISHED":
                response["winner_id"] = room.get("winner_id")

            return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("poll_room error for room=%s user=%s: %s", room_id, me, e)
        raise HTTPException(status_code=500, detail=f"Oda durumu alınırken hata: {e}")


@router.post("/rooms/{room_id}/join")
async def join_room(room_id: str, user: dict = Depends(verify_user)):
    """Oda kodunu bilen herkes katılabilir."""
    me = user["user_id"]

    try:
        async with _db_conn(cache.db_path, user_data=True) as db:
            room = await _get_room(db, room_id)

            if room["status"] != "WAITING":
                raise HTTPException(status_code=400, detail="Oda artık katılıma açık değil")
            if room["creator_id"] == me:
                return {"ok": True, "status": "WAITING"}
            if room["opponent_id"] and room["opponent_id"] != me:
                raise HTTPException(status_code=400, detail="Odada zaten bir rakip var")

            await db.execute(
                "UPDATE quiz_rooms SET opponent_id = ? WHERE id = ?",
                (me, room_id),
            )
            await db.commit()

        return {"ok": True, "status": "WAITING"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("join_room error for room=%s user=%s: %s", room_id, me, e)
        raise HTTPException(status_code=500, detail=f"Odaya katılırken hata: {e}")


@router.post("/rooms/{room_id}/ready")
async def toggle_ready(room_id: str, user: dict = Depends(verify_user)):
    """Hazır durumunu toggle et."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)

        if room["status"] not in ("WAITING", "READY"):
            raise HTTPException(status_code=400, detail="Oyun zaten başladı")
        if me not in (room["creator_id"], room["opponent_id"]):
            raise HTTPException(status_code=403, detail="Bu odada değilsin")

        is_creator = me == room["creator_id"]
        col = "creator_ready" if is_creator else "opponent_ready"
        current = room[col]
        new_val = 0 if current else 1

        await db.execute(f"UPDATE quiz_rooms SET {col} = ? WHERE id = ?", (new_val, room_id))

        other_col = "opponent_ready" if is_creator else "creator_ready"
        other_ready = room[other_col]
        new_status = "READY" if (new_val and other_ready) else "WAITING"
        await db.execute("UPDATE quiz_rooms SET status = ? WHERE id = ?", (new_status, room_id))
        await db.commit()

    return {"ok": True, "ready": bool(new_val), "status": new_status}


@router.post("/rooms/{room_id}/start")
async def start_game(room_id: str, user: dict = Depends(verify_user)):
    """Kurucu oyunu başlatır. İkisi de hazır olmalı."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)

        if room["creator_id"] != me:
            raise HTTPException(status_code=403, detail="Sadece oda kurucusu başlatabilir")
        if not room["opponent_id"]:
            raise HTTPException(status_code=400, detail="Rakip henüz katılmadı")
        if not room["creator_ready"] or not room["opponent_ready"]:
            raise HTTPException(status_code=400, detail="Her iki oyuncu da hazır olmalı")
        if room["status"] == "PLAYING":
            raise HTTPException(status_code=400, detail="Oyun zaten başladı")

        categories = json.loads(room["categories"]) if isinstance(room["categories"], str) else room["categories"]
        questions = _generate_questions_from_trivia(categories)

        if len(questions) < QUESTIONS_PER_GAME:
            raise HTTPException(
                status_code=500,
                detail=f"Yeterli soru üretilemedi ({len(questions)}/{QUESTIONS_PER_GAME})",
            )

        for q in questions:
            await db.execute(
                """INSERT INTO quiz_questions
                   (room_id, question_index, question_type, category_slug, tmdb_id,
                    question_text, correct_answer, options, hint_image, extra_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    room_id, q["question_index"], q["question_type"], q["category_slug"],
                    q["tmdb_id"], q["question_text"], q["correct_answer"],
                    q["options"], q.get("hint_image"), q.get("extra_data"),
                ),
            )

        started = _now_iso()
        await db.execute(
            """UPDATE quiz_rooms SET status = 'PLAYING', current_question = 0,
               question_started_at = ? WHERE id = ?""",
            (started, room_id),
        )
        await db.commit()

    return {"ok": True, "status": "PLAYING"}


@router.post("/rooms/{room_id}/joker")
async def use_joker(room_id: str, body: JokerBody, user: dict = Depends(verify_user)):
    me = user["user_id"]
    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)
        if room["status"] != "PLAYING":
            raise HTTPException(status_code=400, detail="Oyun aktif değil")
        if me not in (room["creator_id"], room["opponent_id"]):
            raise HTTPException(status_code=403, detail="Bu odada değilsin")
        if body.question_index != room["current_question"]:
            raise HTTPException(status_code=400, detail="Yanlış soru index'i")
        
        jokers = json.loads(room.get("player_jokers") or "{}")
        my_jokers = jokers.setdefault(str(me), {})
        
        if body.joker_type in my_jokers:
            raise HTTPException(status_code=400, detail="Bu joker zaten kullanılmış")
            
        my_jokers[body.joker_type] = body.question_index
        
        await db.execute("UPDATE quiz_rooms SET player_jokers = ? WHERE id = ?", (json.dumps(jokers), room_id))
        await db.commit()
        
        eliminated = []
        poster_url = None
        if body.joker_type == "fifty_fifty":
            cur_q = await db.execute("SELECT options, correct_answer FROM quiz_questions WHERE room_id = ? AND question_index = ?", (room_id, body.question_index))
            q_row = await cur_q.fetchone()
            if q_row:
                options = json.loads(q_row[0])
                correct = q_row[1]
                wrong_opts = [o for o in options if o != correct]
                if len(wrong_opts) >= 2:
                    import random
                    eliminated = random.sample(wrong_opts, 2)
        elif body.joker_type == "poster_hint":
            cur_q = await db.execute(
                "SELECT extra_data FROM quiz_questions WHERE room_id = ? AND question_index = ?",
                (room_id, body.question_index),
            )
            q_row = await cur_q.fetchone()
            if q_row:
                extra = json.loads(q_row[0] or "{}")
                movie_title = extra.get("movie", "")
                if movie_title:
                    cur_p = await db.execute(
                        "SELECT poster_url FROM movie_repository WHERE title LIKE ? LIMIT 1",
                        (f"%{movie_title}%",),
                    )
                    p_row = await cur_p.fetchone()
                    if p_row and p_row[0]:
                        poster_url = p_row[0]

        return {"ok": True, "eliminated": eliminated, "poster_url": poster_url}

@router.post("/rooms/{room_id}/answer")
async def submit_answer(room_id: str, body: AnswerBody, user: dict = Depends(verify_user)):
    """Soru cevabı gönder."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)

        if room["status"] != "PLAYING":
            raise HTTPException(status_code=400, detail="Oyun aktif değil")
        if me not in (room["creator_id"], room["opponent_id"]):
            raise HTTPException(status_code=403, detail="Bu odada değilsin")
        if body.question_index != room["current_question"]:
            raise HTTPException(status_code=400, detail="Yanlış soru index'i")

        jokers = json.loads(room.get("player_jokers") or "{}")
        my_jokers = jokers.get(str(me), {})
        
        has_freeze_time = my_jokers.get("freeze_time") == body.question_index
        max_time_ms = QUESTION_TIME_MS + (10000 if has_freeze_time else 0)
        
        existing_cur = await db.execute(
            "SELECT id, is_correct FROM quiz_answers WHERE room_id = ? AND question_index = ? AND user_id = ?",
            (room_id, body.question_index, me),
        )
        existing = await existing_cur.fetchone()
        
        has_double_chance = my_jokers.get("double_chance") == body.question_index
        
        if existing:
            if existing[1] == 1 or not has_double_chance:
                raise HTTPException(status_code=400, detail="Bu soruyu zaten cevapladın")
        
        started_at = room.get("question_started_at", "")
        elapsed_ms = max_time_ms
        if started_at:
            started_ms = int(datetime.fromisoformat(started_at).timestamp() * 1000)
            elapsed_ms = min(max_time_ms, max(0, _now_ms() - started_ms))

        if elapsed_ms > max_time_ms + 2000:
            raise HTTPException(status_code=400, detail="Süre doldu")

        cur_q = await db.execute(
            "SELECT correct_answer FROM quiz_questions WHERE room_id = ? AND question_index = ?",
            (room_id, body.question_index),
        )
        q_row = await cur_q.fetchone()
        if not q_row:
            raise HTTPException(status_code=500, detail="Soru bulunamadı")

        correct_answer = q_row[0]
        is_correct = body.selected_answer == correct_answer
        
        cur_streak = await db.execute("SELECT is_correct FROM quiz_answers WHERE room_id = ? AND user_id = ? AND question_index < ? ORDER BY question_index ASC", (room_id, me, body.question_index))
        streak_rows = await cur_streak.fetchall()
        streak_count = 0
        for r in streak_rows:
            if r[0]: streak_count += 1
            else: streak_count = 0
            
        base_score = _calculate_score(elapsed_ms) if is_correct else 0
        if existing and is_correct:
            base_score = 10 # Cezalı puan
            
        score = base_score
        is_combo = False
        if is_correct and streak_count >= 2:
            score = int(score * 1.5)
            is_combo = True
            
        if existing:
            await db.execute(
                "UPDATE quiz_answers SET selected_answer = ?, is_correct = ?, elapsed_ms = ?, score = ? WHERE id = ?",
                (body.selected_answer, int(is_correct), elapsed_ms, score, existing[0]),
            )
        else:
            await db.execute(
                """INSERT INTO quiz_answers
                   (room_id, question_index, user_id, selected_answer, is_correct, elapsed_ms, score)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (room_id, body.question_index, me, body.selected_answer, int(is_correct), elapsed_ms, score),
            )
        await db.commit()

        cur_cnt = await db.execute(
            "SELECT COUNT(*) FROM quiz_answers WHERE room_id = ? AND question_index = ?",
            (room_id, body.question_index),
        )
        both_answered = (await cur_cnt.fetchone())[0] >= 2

        if both_answered:
            room = await _get_room(db, room_id)
            await _check_advance_question(db, room)

        can_retry = has_double_chance and not is_correct and not existing
        return {
            "is_correct": is_correct,
            "correct_answer": None if can_retry else correct_answer,
            "score": score,
            "elapsed_ms": elapsed_ms,
            "both_answered": both_answered,
        }


@router.get("/rooms/{room_id}/results")
async def get_results(room_id: str, user: dict = Depends(verify_user)):
    """Oyun sonu detaylı sonuçlar."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)

        if me not in (room["creator_id"], room["opponent_id"]):
            raise HTTPException(status_code=403, detail="Bu odada değilsin")

        creator_info = await _user_info(room["creator_id"])
        opponent_info = await _user_info(room["opponent_id"]) if room["opponent_id"] else None

        cur_q = await db.execute(
            """SELECT question_index, question_type, question_text, correct_answer,
                      options, hint_image, tmdb_id
               FROM quiz_questions WHERE room_id = ? ORDER BY question_index""",
            (room_id,),
        )
        q_rows = await cur_q.fetchall()

        cur_a = await db.execute(
            """SELECT question_index, user_id, selected_answer, is_correct, elapsed_ms, score
               FROM quiz_answers WHERE room_id = ? ORDER BY question_index""",
            (room_id,),
        )
        a_rows = await cur_a.fetchall()

        answers_map: dict[int, dict[int, dict]] = {}
        for a in a_rows:
            qi, uid = a[0], a[1]
            if qi not in answers_map:
                answers_map[qi] = {}
            answers_map[qi][uid] = {
                "selected": a[2], "is_correct": bool(a[3]),
                "elapsed_ms": a[4], "score": a[5],
            }

        questions_detail = []
        for q in q_rows:
            qi = q[0]
            q_answers = answers_map.get(qi, {})
            questions_detail.append({
                "index": qi,
                "type": q[1],
                "text": q[2],
                "correct_answer": q[3],
                "options": json.loads(q[4]),
                "hint_image": q[5],
                "tmdb_id": q[6],
                "creator_answer": q_answers.get(room["creator_id"]),
                "opponent_answer": q_answers.get(room["opponent_id"]),
            })

        total_scores = {}
        total_correct = {}
        for uid in (room["creator_id"], room["opponent_id"]):
            if uid:
                cur_s = await db.execute(
                    "SELECT SUM(score), SUM(is_correct) FROM quiz_answers WHERE room_id = ? AND user_id = ?",
                    (room_id, uid),
                )
                s_row = await cur_s.fetchone()
                total_scores[uid] = s_row[0] or 0 if s_row else 0
                total_correct[uid] = s_row[1] or 0 if s_row else 0

        categories = json.loads(room["categories"]) if isinstance(room["categories"], str) else room["categories"]
        cat_labels = []
        for cs in categories:
            cat_def = QUIZ_CATEGORIES.get(cs)
            cat_labels.append({
                "slug": cs,
                "label": cat_def["label"] if cat_def else cs,
                "emoji": cat_def["emoji"] if cat_def else "",
            })

        elo_changes = None
        c_before = room.get("creator_elo_before")
        if c_before is not None:
            c_after = room.get("creator_elo_after") or c_before
            o_before = room.get("opponent_elo_before") or 1000
            o_after = room.get("opponent_elo_after") or o_before
            elo_changes = {
                "creator": {"before": c_before, "after": c_after, "delta": c_after - c_before,
                            "league": _get_league(c_after)},
                "opponent": {"before": o_before, "after": o_after, "delta": o_after - o_before,
                             "league": _get_league(o_after)},
            }

        return {
            "room_id": room_id,
            "status": room["status"],
            "winner_id": room.get("winner_id"),
            "is_draw": room.get("winner_id") is None and room["status"] == "FINISHED",
            "creator": {
                **creator_info,
                "total_score": total_scores.get(room["creator_id"], 0),
                "total_correct": total_correct.get(room["creator_id"], 0),
            },
            "opponent": {
                **(opponent_info or {}),
                "total_score": total_scores.get(room["opponent_id"], 0),
                "total_correct": total_correct.get(room["opponent_id"], 0),
            } if opponent_info else None,
            "categories": cat_labels,
            "questions": questions_detail,
            "elo_changes": elo_changes,
        }


@router.post("/rooms/{room_id}/rematch")
async def rematch(room_id: str, user: dict = Depends(verify_user)):
    """Aynı kategoriler ve rakiple yeni oda oluştur."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)

        if room["status"] != "FINISHED":
            raise HTTPException(status_code=400, detail="Oyun henüz bitmedi")

        if me not in (room["creator_id"], room["opponent_id"]):
            raise HTTPException(status_code=403, detail="Bu odada değilsin")

        categories = json.loads(room["categories"]) if isinstance(room["categories"], str) else room["categories"]
        other_id = room["opponent_id"] if me == room["creator_id"] else room["creator_id"]

        new_room_id = uuid.uuid4().hex[:6].upper()
        await db.execute(
            """INSERT INTO quiz_rooms (id, creator_id, opponent_id, categories, status)
               VALUES (?, ?, ?, ?, 'WAITING')""",
            (new_room_id, me, other_id, json.dumps(categories)),
        )
        await db.commit()

    return {"room_id": new_room_id, "categories": categories, "status": "WAITING"}


@router.post("/rooms/{room_id}/leave")
async def leave_room(room_id: str, user: dict = Depends(verify_user)):
    """Odadan ayrıl / terk et."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)

        if me not in (room["creator_id"], room["opponent_id"]):
            raise HTTPException(status_code=403, detail="Bu odada değilsin")

        if room["status"] in ("FINISHED", "ABANDONED"):
            return {"ok": True, "status": room["status"]}

        if room["status"] == "PLAYING":
            opponent_id = room["opponent_id"] if me == room["creator_id"] else room["creator_id"]
            await db.execute(
                """UPDATE quiz_rooms SET status = 'FINISHED', winner_id = ?,
                   finished_at = CURRENT_TIMESTAMP WHERE id = ?""",
                (opponent_id, room_id),
            )
            await _update_stats(db, room_id, room["creator_id"], room["opponent_id"], opponent_id)
        else:
            await db.execute(
                "UPDATE quiz_rooms SET status = 'ABANDONED', finished_at = CURRENT_TIMESTAMP WHERE id = ?",
                (room_id,),
            )
        await db.commit()

    return {"ok": True, "status": "ABANDONED"}


@router.get("/stats")
async def get_stats(user: dict = Depends(verify_user)):
    """Kullanıcı düello istatistikleri."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        cur = await db.execute(
            "SELECT user_id, games_played, games_won, total_score, best_score, win_streak, best_streak, elo_rating, elo_peak FROM quiz_stats WHERE user_id = ?",
            (me,),
        )
        row = await cur.fetchone()

        if not row:
            return {
                "games_played": 0, "games_won": 0,
                "total_score": 0, "best_score": 0,
                "win_streak": 0, "best_streak": 0,
                "win_rate": 0,
                "elo_rating": 1000, "elo_peak": 1000,
                "league": _get_league(1000),
            }

        stat_cols = ["user_id", "games_played", "games_won", "total_score", "best_score", "win_streak", "best_streak", "elo_rating", "elo_peak"]
        stats = dict(zip(stat_cols, row))
        stats["elo_rating"] = stats.get("elo_rating") or 1000
        stats["elo_peak"] = stats.get("elo_peak") or 1000
        stats["league"] = _get_league(stats["elo_rating"])
        stats["win_rate"] = round(
            (stats["games_won"] / stats["games_played"] * 100)
            if stats["games_played"] > 0 else 0
        )
        return stats


@router.get("/history")
async def get_history(user: dict = Depends(verify_user), limit: int = 20):
    """Son oyunlar listesi."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        cur = await db.execute(
            """SELECT r.id, r.creator_id, r.opponent_id, r.status, r.winner_id,
                      r.categories, r.created_at, r.finished_at
               FROM quiz_rooms r
               WHERE (r.creator_id = ? OR r.opponent_id = ?)
                 AND r.status IN ('FINISHED', 'ABANDONED')
               ORDER BY r.finished_at DESC LIMIT ?""",
            (me, me, limit),
        )
        rows = await cur.fetchall()

        games = []
        for r in rows:
            creator_id, opponent_id = r[1], r[2]
            other_id = opponent_id if creator_id == me else creator_id
            other_info = await _user_info(other_id) if other_id else None

            cur_s = await db.execute(
                "SELECT user_id, SUM(score) FROM quiz_answers WHERE room_id = ? GROUP BY user_id",
                (r[0],),
            )
            score_rows = await cur_s.fetchall()
            scores = {sr[0]: sr[1] or 0 for sr in score_rows}

            games.append({
                "room_id": r[0],
                "opponent": other_info,
                "status": r[3],
                "winner_id": r[4],
                "i_won": r[4] == me,
                "is_draw": r[4] is None and r[3] == "FINISHED",
                "my_score": scores.get(me, 0),
                "opponent_score": scores.get(other_id, 0),
                "categories": json.loads(r[5]) if r[5] else [],
                "played_at": r[7] or r[6],
            })

        return {"games": games}


# ─── Bekleyen Davet Kontrolü ────────────────────────────────────────────────

@router.get("/pending-invite")
async def check_pending_invite(user: dict = Depends(verify_user)):
    """Kullanıcıya gelen bekleyen düello daveti var mı?"""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        cur = await db.execute(
            """SELECT id, creator_id, categories, created_at
               FROM quiz_rooms
               WHERE opponent_id = ? AND status = 'WAITING'
               ORDER BY created_at DESC LIMIT 1""",
            (me,),
        )
        row = await cur.fetchone()
        if not row:
            return {"has_invite": False}

        creator_info = await _user_info(row[1])
        return {
            "has_invite": True,
            "room_id": row[0],
            "creator": creator_info,
            "categories": json.loads(row[2]) if row[2] else [],
            "created_at": row[3],
        }


# ─── Matchmaking ────────────────────────────────────────────────────────────

class MatchmakingBody(BaseModel):
    categories: list[str] = Field(..., min_length=1, max_length=3)


@router.post("/matchmaking/join")
async def join_matchmaking(body: MatchmakingBody, user: dict = Depends(verify_user)):
    """Eşleşme kuyruğuna gir. Anında eşleşme varsa oda döner."""
    me = user["user_id"]

    for cat in body.categories:
        if cat != "rastgele" and cat not in QUIZ_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Geçersiz kategori: {cat}")

    all_cats = list(body.categories)
    if "rastgele" in all_cats:
        all_cats.remove("rastgele")
        remaining = [k for k in QUIZ_CATEGORIES if k not in all_cats]
        if remaining:
            all_cats.append(random.choice(remaining))

    async with _db_conn(cache.db_path, user_data=True) as db:
        my_elo, _ = await _get_elo(db, me)

        await db.execute(
            "INSERT OR REPLACE INTO quiz_matchmaking_queue (user_id, elo_rating, categories, joined_at) VALUES (?, ?, ?, datetime('now'))",
            (me, my_elo, json.dumps(all_cats)),
        )
        await db.commit()

        match = await _try_match(db, me, my_elo, all_cats, elo_range=200)
        if match:
            return match

    return {"matched": False}


@router.get("/matchmaking/poll")
async def poll_matchmaking(user: dict = Depends(verify_user)):
    """Eşleşme kuyruğunu poll et."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        cur = await db.execute(
            "SELECT elo_rating, categories, joined_at FROM quiz_matchmaking_queue WHERE user_id = ?",
            (me,),
        )
        row = await cur.fetchone()

        if not row:
            cur2 = await db.execute(
                """SELECT id FROM quiz_rooms
                   WHERE opponent_id = ? AND status = 'WAITING'
                   ORDER BY created_at DESC LIMIT 1""",
                (me,),
            )
            room_row = await cur2.fetchone()
            if room_row:
                return {"matched": True, "room_id": room_row[0]}
            return {"matched": False, "timeout": True}

        my_elo = row[0] or 1000
        my_cats = json.loads(row[1]) if row[1] else []
        joined_at = row[2]

        try:
            joined_dt = datetime.fromisoformat(joined_at.replace("Z", "+00:00")) if joined_at else datetime.now(timezone.utc)
        except Exception:
            joined_dt = datetime.now(timezone.utc)

        elapsed_s = (datetime.now(timezone.utc) - joined_dt.replace(tzinfo=timezone.utc if joined_dt.tzinfo is None else joined_dt.tzinfo)).total_seconds()

        if elapsed_s > 120:
            await db.execute("DELETE FROM quiz_matchmaking_queue WHERE user_id = ?", (me,))
            await db.commit()
            return {"matched": False, "timeout": True}

        if elapsed_s <= 10:
            elo_range = 200
        elif elapsed_s <= 30:
            elo_range = 400
        elif elapsed_s <= 60:
            elo_range = 600
        else:
            elo_range = 800

        match = await _try_match(db, me, my_elo, my_cats, elo_range)
        if match:
            return match

    return {"matched": False, "elapsed": round(elapsed_s)}


@router.post("/matchmaking/leave")
async def leave_matchmaking(user: dict = Depends(verify_user)):
    """Eşleşme kuyruğundan çık."""
    me = user["user_id"]
    async with _db_conn(cache.db_path, user_data=True) as db:
        await db.execute("DELETE FROM quiz_matchmaking_queue WHERE user_id = ?", (me,))
        await db.commit()
    return {"ok": True}


async def _try_match(db, me: int, my_elo: int, my_cats: list, elo_range: int) -> Optional[dict]:
    cur = await db.execute(
        """SELECT user_id, elo_rating, categories FROM quiz_matchmaking_queue
           WHERE user_id != ? AND ABS(elo_rating - ?) <= ?
           ORDER BY ABS(elo_rating - ?) ASC LIMIT 1""",
        (me, my_elo, elo_range, my_elo),
    )
    row = await cur.fetchone()
    if not row:
        return None

    other_id = row[0]
    other_cats = json.loads(row[2]) if row[2] else []

    shared = set(my_cats) & set(other_cats)
    if not shared:
        union = list(set(my_cats) | set(other_cats))
        cats = random.sample(union, min(3, len(union)))
    else:
        cats = list(shared)[:3]

    await db.execute("DELETE FROM quiz_matchmaking_queue WHERE user_id IN (?, ?)", (me, other_id))

    room_id = uuid.uuid4().hex[:6].upper()
    await db.execute(
        """INSERT INTO quiz_rooms (id, creator_id, opponent_id, categories, status)
           VALUES (?, ?, ?, ?, 'WAITING')""",
        (room_id, me, other_id, json.dumps(cats)),
    )
    await db.commit()

    return {"matched": True, "room_id": room_id, "categories": cats}


# ─── Leaderboard ────────────────────────────────────────────────────────────

@router.get("/leaderboard")
async def get_leaderboard(user: dict = Depends(verify_user), limit: int = 50):
    """Top oyuncular ELO sıralamasına göre."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        cur = await db.execute(
            """SELECT s.user_id, s.elo_rating, s.games_played, s.games_won,
                      u.username, u.name, u.picture
               FROM quiz_stats s JOIN users u ON s.user_id = u.id
               WHERE s.games_played >= 1
               ORDER BY COALESCE(s.elo_rating, 1000) DESC LIMIT ?""",
            (limit,),
        )
        rows = await cur.fetchall()

        players = []
        for i, r in enumerate(rows):
            elo = r[1] or 1000
            played = r[2] or 0
            won = r[3] or 0
            players.append({
                "rank": i + 1,
                "user_id": r[0],
                "username": r[4] or "",
                "name": r[5] or "",
                "avatar": r[6],
                "elo_rating": elo,
                "league": _get_league(elo),
                "games_played": played,
                "games_won": won,
                "win_rate": round(won / played * 100) if played > 0 else 0,
            })

        cur_rank = await db.execute(
            "SELECT COUNT(*) FROM quiz_stats WHERE COALESCE(elo_rating, 1000) > (SELECT COALESCE(elo_rating, 1000) FROM quiz_stats WHERE user_id = ?)",
            (me,),
        )
        rank_row = await cur_rank.fetchone()
        my_rank = (rank_row[0] + 1) if rank_row else None

    return {"players": players, "my_rank": my_rank}


# ─── Oda Temizleme (background task olarak main.py'den çağrılır) ────────────

async def cleanup_stale_rooms():
    """10dk'dan eski WAITING ve 2 saattten eski PLAYING odaları ABANDONED yap."""
    try:
        async with _db_conn(cache.db_path, user_data=True) as db:
            await db.execute(
                """UPDATE quiz_rooms SET status = 'ABANDONED', finished_at = CURRENT_TIMESTAMP
                   WHERE status = 'WAITING'
                     AND created_at < datetime('now', '-10 minutes')""",
            )
            await db.execute(
                """UPDATE quiz_rooms SET status = 'ABANDONED', finished_at = CURRENT_TIMESTAMP
                   WHERE status IN ('PLAYING', 'READY')
                     AND created_at < datetime('now', '-2 hours')""",
            )
            await db.execute(
                "DELETE FROM quiz_matchmaking_queue WHERE joined_at < datetime('now', '-3 minutes')",
            )
            await db.commit()
    except Exception as e:
        logger.warning("[Quiz] Cleanup error: %s", e)
