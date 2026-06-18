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
    categories: list[str] = Field(..., min_length=3, max_length=3)
    opponent_id: int

class AnswerBody(BaseModel):
    question_index: int
    selected_answer: str


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


async def _get_room(db, room_id: str) -> dict:
    cur = await db.execute("SELECT * FROM quiz_rooms WHERE id = ?", (room_id,))
    row = await cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Oda bulunamadı")
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


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


# ─── Soru Üretim Motoru ─────────────────────────────────────────────────────

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


QUESTION_TYPES = [
    "mood_guess", "director_match", "year_guess",
    "cast_id", "plot_match", "rating_range", "poster_recognize",
]


async def _generate_questions(categories: list[str]) -> list[dict]:
    """10 soru üret: ilk 3 kategoriden 3'er, rastgele kategoriden 1."""
    all_films_by_cat: dict[str, list] = {}
    for cat_slug in categories:
        films = await _fetch_films_for_category(cat_slug, limit=80)
        if films:
            all_films_by_cat[cat_slug] = films

    if not all_films_by_cat:
        raise HTTPException(status_code=500, detail="Yeterli film bulunamadı")

    all_films_flat = []
    for films in all_films_by_cat.values():
        all_films_flat.extend(films)

    all_directors = set()
    all_actors = set()
    all_titles = set()
    for f in all_films_flat:
        all_titles.add(f["title"])

    distribution = []
    for i, cat_slug in enumerate(categories[:3]):
        distribution.extend([(cat_slug, 3)])
    if len(categories) > 3:
        distribution.append((categories[3], 1))

    questions = []
    used_tmdb_ids = set()
    type_counts: dict[str, int] = {}

    for cat_slug, count in distribution:
        cat_films = all_films_by_cat.get(cat_slug, [])
        if not cat_films:
            continue

        random.shuffle(cat_films)

        generated = 0
        for film in cat_films:
            if generated >= count:
                break
            if film["tmdb_id"] in used_tmdb_ids:
                continue

            available_types = [
                t for t in QUESTION_TYPES
                if type_counts.get(t, 0) < 2
            ]
            if not available_types:
                available_types = QUESTION_TYPES[:]

            random.shuffle(available_types)

            q = None
            for qtype in available_types:
                q = await _build_question(
                    qtype, film, cat_slug, all_films_flat, used_tmdb_ids,
                    all_directors, all_actors,
                )
                if q:
                    type_counts[qtype] = type_counts.get(qtype, 0) + 1
                    break

            if q:
                questions.append(q)
                used_tmdb_ids.add(film["tmdb_id"])
                generated += 1

    while len(questions) < QUESTIONS_PER_GAME:
        remaining_films = [
            f for cat_films in all_films_by_cat.values()
            for f in cat_films
            if f["tmdb_id"] not in used_tmdb_ids
        ]
        if not remaining_films:
            break
        film = random.choice(remaining_films)
        cat_slug = categories[0]
        available_types = [t for t in QUESTION_TYPES if type_counts.get(t, 0) < 3]
        if not available_types:
            available_types = QUESTION_TYPES[:]
        random.shuffle(available_types)
        for qtype in available_types:
            q = await _build_question(
                qtype, film, cat_slug, all_films_flat, used_tmdb_ids,
                all_directors, all_actors,
            )
            if q:
                questions.append(q)
                used_tmdb_ids.add(film["tmdb_id"])
                type_counts[qtype] = type_counts.get(qtype, 0) + 1
                break
        else:
            used_tmdb_ids.add(film["tmdb_id"])

    random.shuffle(questions)

    for i, q in enumerate(questions):
        q["question_index"] = i

    return questions[:QUESTIONS_PER_GAME]


async def _build_question(
    qtype: str, film: dict, cat_slug: str,
    all_films: list, used_ids: set,
    all_directors: set, all_actors: set,
) -> Optional[dict]:
    """Tek bir soru üret. Başarısızsa None döndürür."""
    tmdb_id = film["tmdb_id"]
    title = film["title"]
    year = (film.get("release_date") or "")[:4]
    poster = film.get("poster_url", "")
    overview = (film.get("overview") or "")[:200]
    rating = film.get("vote_average", 0)
    mood_id = film.get("mood_id", "")

    other_films = [
        f for f in all_films
        if f["tmdb_id"] != tmdb_id and f["tmdb_id"] not in used_ids
    ]

    base = {
        "question_type": qtype,
        "category_slug": cat_slug,
        "tmdb_id": tmdb_id,
        "hint_image": None,
        "extra_data": None,
    }

    if qtype == "mood_guess":
        if not mood_id or mood_id not in MOOD_ID_LABELS:
            return None
        correct = MOOD_ID_LABELS[mood_id]
        distractors = [v for k, v in MOOD_ID_LABELS.items() if k != mood_id]
        random.shuffle(distractors)
        options = [correct] + distractors[:3]
        random.shuffle(options)
        return {
            **base,
            "question_text": f'"{title}" filmi hangi ruh haline ait?',
            "correct_answer": correct,
            "options": json.dumps(options, ensure_ascii=False),
            "hint_image": poster,
        }

    elif qtype == "director_match":
        credits = await _get_credits(tmdb_id)
        director = credits.get("director", "")
        if not director:
            return None
        all_directors.add(director)
        distractor_dirs = list(all_directors - {director})
        if len(distractor_dirs) < 3:
            for of in other_films[:20]:
                oc = await _get_credits(of["tmdb_id"])
                d = oc.get("director", "")
                if d and d != director:
                    distractor_dirs.append(d)
                    all_directors.add(d)
                if len(distractor_dirs) >= 6:
                    break
        if len(distractor_dirs) < 3:
            return None
        random.shuffle(distractor_dirs)
        options = [director] + distractor_dirs[:3]
        random.shuffle(options)
        return {
            **base,
            "question_text": f'"{title}" filminin yönetmeni kimdir?',
            "correct_answer": director,
            "options": json.dumps(options, ensure_ascii=False),
            "hint_image": poster,
        }

    elif qtype == "year_guess":
        if not year or not year.isdigit():
            return None
        y = int(year)
        offsets = [-4, -2, 2, 4]
        random.shuffle(offsets)
        distractors = []
        for off in offsets:
            dy = str(y + off)
            if dy not in distractors and dy != year:
                distractors.append(dy)
            if len(distractors) == 3:
                break
        if len(distractors) < 3:
            return None
        options = [year] + distractors
        random.shuffle(options)
        return {
            **base,
            "question_text": f'"{title}" filmi hangi yılda vizyona girdi?',
            "correct_answer": year,
            "options": json.dumps(options, ensure_ascii=False),
            "hint_image": poster,
        }

    elif qtype == "cast_id":
        credits = await _get_credits(tmdb_id)
        cast = credits.get("cast", [])
        if not cast:
            return None
        correct_actor = cast[0]["name"]
        all_actors.add(correct_actor)
        for a in cast:
            all_actors.add(a["name"])
        distractor_actors = list(all_actors - {correct_actor})
        if len(distractor_actors) < 3:
            for of in other_films[:15]:
                oc = await _get_credits(of["tmdb_id"])
                for a in oc.get("cast", []):
                    if a["name"] != correct_actor:
                        distractor_actors.append(a["name"])
                        all_actors.add(a["name"])
                if len(distractor_actors) >= 6:
                    break
        film_actor_names = {a["name"] for a in cast}
        distractor_actors = [a for a in distractor_actors if a not in film_actor_names]
        if len(distractor_actors) < 3:
            return None
        random.shuffle(distractor_actors)
        options = [correct_actor] + distractor_actors[:3]
        random.shuffle(options)
        return {
            **base,
            "question_text": f'Aşağıdaki oyunculardan hangisi "{title}" filminde rol almıştır?',
            "correct_answer": correct_actor,
            "options": json.dumps(options, ensure_ascii=False),
            "hint_image": poster,
        }

    elif qtype == "plot_match":
        if not overview or len(overview) < 30:
            return None
        distractor_titles = [
            f["title"] for f in other_films
            if f["title"] != title and f.get("overview") and len(f["overview"]) > 30
        ]
        if len(distractor_titles) < 3:
            return None
        random.shuffle(distractor_titles)
        options = [title] + distractor_titles[:3]
        random.shuffle(options)
        display_overview = overview[:150]
        if len(overview) > 150:
            display_overview = display_overview.rsplit(" ", 1)[0] + "..."
        return {
            **base,
            "question_text": f"Hangi filmin konusu bu?\n\n\"{display_overview}\"",
            "correct_answer": title,
            "options": json.dumps(options, ensure_ascii=False),
        }

    elif qtype == "rating_range":
        if not rating or rating < 1:
            return None
        r = round(rating, 1)
        if r >= 8.5:
            ranges = ["7.0 – 7.9", "8.0 – 8.4", "8.5 – 9.0", "9.0 – 10.0"]
            correct = "8.5 – 9.0" if r < 9.0 else "9.0 – 10.0"
        elif r >= 8.0:
            ranges = ["6.5 – 7.4", "7.5 – 7.9", "8.0 – 8.4", "8.5 – 9.0"]
            correct = "8.0 – 8.4"
        elif r >= 7.0:
            ranges = ["5.5 – 6.4", "6.5 – 6.9", "7.0 – 7.4", "7.5 – 8.0"]
            correct = "7.0 – 7.4" if r < 7.5 else "7.5 – 8.0"
        elif r >= 6.0:
            ranges = ["4.5 – 5.4", "5.5 – 5.9", "6.0 – 6.4", "6.5 – 7.0"]
            correct = "6.0 – 6.4" if r < 6.5 else "6.5 – 7.0"
        else:
            ranges = ["3.0 – 4.4", "4.5 – 5.4", "5.5 – 5.9", "6.0 – 6.5"]
            correct = "4.5 – 5.4" if r >= 4.5 else "3.0 – 4.4"
        return {
            **base,
            "question_text": f'"{title}" filminin IMDb puanı hangi aralıkta?',
            "correct_answer": correct,
            "options": json.dumps(ranges, ensure_ascii=False),
            "hint_image": poster,
        }

    elif qtype == "poster_recognize":
        if not poster:
            return None
        distractor_titles = [
            f["title"] for f in other_films
            if f["title"] != title and f.get("poster_url")
        ]
        if len(distractor_titles) < 3:
            return None
        random.shuffle(distractor_titles)
        options = [title] + distractor_titles[:3]
        random.shuffle(options)
        return {
            **base,
            "question_text": "Bu poster hangi filme ait?",
            "correct_answer": title,
            "options": json.dumps(options, ensure_ascii=False),
            "hint_image": poster,
            "extra_data": json.dumps({"blur": True}, ensure_ascii=False),
        }

    return None


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
        await db.execute(
            """UPDATE quiz_rooms SET status = 'FINISHED', current_question = ?,
               winner_id = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?""",
            (q_idx, winner_id, room["id"]),
        )
        await db.commit()
        await _update_stats(db, room["id"], room["creator_id"], room["opponent_id"], winner_id)
        room["status"] = "FINISHED"
        room["winner_id"] = winner_id
    else:
        new_started = _now_iso()
        await db.execute(
            "UPDATE quiz_rooms SET current_question = ?, question_started_at = ? WHERE id = ?",
            (next_q, new_started, room["id"]),
        )
        await db.commit()
        room["current_question"] = next_q
        room["question_started_at"] = new_started

    return room


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

        cur2 = await db.execute("SELECT * FROM quiz_stats WHERE user_id = ?", (uid,))
        existing = await cur2.fetchone()

        if existing:
            cols = [d[0] for d in cur2.description]
            stats = dict(zip(cols, existing))
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
                   best_score, win_streak, best_streak)
                   VALUES (?, 1, ?, ?, ?, ?, ?)""",
                (uid, won, game_score, game_score, 1 if won else 0, 1 if won else 0),
            )
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
    """Oda oluştur. 3 kategori seç, 1 rastgele eklenir."""
    me = user["user_id"]
    opponent_id = body.opponent_id

    if opponent_id == me:
        raise HTTPException(status_code=400, detail="Kendinle oynayamazsın")

    is_friend = await cache.are_friends(me, opponent_id)
    if not is_friend:
        raise HTTPException(status_code=403, detail="Sadece arkadaşlarınla oynayabilirsin")

    for cat in body.categories:
        if cat not in QUIZ_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Geçersiz kategori: {cat}")

    remaining = [k for k in QUIZ_CATEGORIES if k not in body.categories]
    random_cat = random.choice(remaining) if remaining else body.categories[0]
    all_cats = list(body.categories) + [random_cat]

    room_id = uuid.uuid4().hex[:8]

    async with _db_conn(cache.db_path, user_data=True) as db:
        await db.execute(
            """INSERT INTO quiz_rooms (id, creator_id, opponent_id, categories, status)
               VALUES (?, ?, ?, ?, 'WAITING')""",
            (room_id, me, opponent_id, json.dumps(all_cats)),
        )
        await db.commit()

    try:
        from backend.services.push_service import send_push_to_user
        sender = await cache.get_user_by_username_by_id(me)
        sender_name = (sender or {}).get("username") or (sender or {}).get("name") or "Biri"
        await send_push_to_user(
            opponent_id,
            "Sinema Düello",
            f"{sender_name} seni Sinema Düello'ya davet ediyor!",
            url=f"/duello?room={room_id}",
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

    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)

        if me not in (room["creator_id"], room["opponent_id"]):
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

        response = {
            "room_id": room_id,
            "status": room["status"],
            "creator": await _user_info(room["creator_id"]),
            "opponent": await _user_info(room["opponent_id"]) if room["opponent_id"] else None,
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

            response.update({
                "current_question": q_idx,
                "total_questions": QUESTIONS_PER_GAME,
                "question": question_data,
                "my_answer": my_answer,
                "opponent_answered": opp_answered,
                "scores": {
                    "me": score_map.get(me, 0),
                    "opponent": score_map.get(opponent_id, 0),
                },
            })

        elif room["status"] == "FINISHED":
            response["winner_id"] = room.get("winner_id")

        return response


@router.post("/rooms/{room_id}/join")
async def join_room(room_id: str, user: dict = Depends(verify_user)):
    """Rakip odaya katılır."""
    me = user["user_id"]

    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)

        if room["status"] != "WAITING":
            raise HTTPException(status_code=400, detail="Oda artık katılıma açık değil")
        if room["opponent_id"] and room["opponent_id"] != me:
            raise HTTPException(status_code=403, detail="Bu oda sana ait değil")
        if room["creator_id"] == me:
            raise HTTPException(status_code=400, detail="Kendi odana katılamazsın")

        await db.execute(
            "UPDATE quiz_rooms SET opponent_id = ? WHERE id = ?",
            (me, room_id),
        )
        await db.commit()

    return {"ok": True, "status": "WAITING"}


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
        questions = await _generate_questions(categories)

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

        existing = await db.execute(
            "SELECT id FROM quiz_answers WHERE room_id = ? AND question_index = ? AND user_id = ?",
            (room_id, body.question_index, me),
        )
        if await existing.fetchone():
            raise HTTPException(status_code=400, detail="Bu soruyu zaten cevapladın")

        started_at = room.get("question_started_at", "")
        elapsed_ms = QUESTION_TIME_MS
        if started_at:
            started_ms = int(datetime.fromisoformat(started_at).timestamp() * 1000)
            elapsed_ms = min(QUESTION_TIME_MS, max(0, _now_ms() - started_ms))

        if elapsed_ms > QUESTION_TIME_MS + 2000:
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
        score = _calculate_score(elapsed_ms) if is_correct else 0

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

    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
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
        }


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
        cur = await db.execute("SELECT * FROM quiz_stats WHERE user_id = ?", (me,))
        row = await cur.fetchone()

        if not row:
            return {
                "games_played": 0, "games_won": 0,
                "total_score": 0, "best_score": 0,
                "win_streak": 0, "best_streak": 0,
                "win_rate": 0,
            }

        cols = [d[0] for d in cur.description]
        stats = dict(zip(cols, row))
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
            await db.commit()
    except Exception as e:
        logger.warning("[Quiz] Cleanup error: %s", e)
