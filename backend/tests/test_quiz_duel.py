"""SineQuiz düello entegrasyon testleri — iki eşzamanlı istemci.

Düello canlı bir durum makinesi: `submit_answer` VE her `poll_room` çağrısı
`_check_advance_question`'ı tetikler. Tek istemcili test bu yüzden yetmez;
buradaki testler iki oyuncunun birbirini nasıl etkilediğini kurar.
"""
import asyncio
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.auth_utils import _create_token
from backend.database import cache, _get_connection as _db_conn

A, B = 1, 2  # oyuncu id'leri


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_quiz.db")
    monkeypatch.setattr(cache, "db_path", db_path)
    import backend.database as dbmod
    monkeypatch.setattr(dbmod, "_turso_client", None)
    monkeypatch.setattr(dbmod, "_pool_init", False)
    asyncio.run(cache.init_db())

    async def _seed():
        async with _db_conn(db_path, user_data=True) as db:
            for gid, uname in (("g1", "ali"), ("g2", "banu")):
                await db.execute(
                    "INSERT INTO users (google_id, email, name, username, picture) VALUES (?,?,?,?,?)",
                    (gid, f"{uname}@x.com", uname.title(), uname, ""),
                )
            await db.commit()
    asyncio.run(_seed())

    # Oda daveti push'u ağa/servise gitmesin
    import backend.services.push_service as ps
    monkeypatch.setattr(ps, "PUSH_ENABLED", False)
    monkeypatch.setattr(ps, "FCM_ENABLED", False)

    from backend.routers.quiz import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def hdr(uid):
    return {"Authorization": f"Bearer {_create_token({'type': 'user', 'user_id': uid}, 1)}"}


# ─── Yardımcılar ─────────────────────────────────────────────────────────────

def start_duel(client):
    """A oda kurar, B katılır, ikisi hazır olur, A başlatır. room_id döner."""
    r = client.post("/api/game/quiz/rooms", json={"categories": ["rastgele"]}, headers=hdr(A))
    assert r.status_code == 200, r.text
    room_id = r.json()["room_id"]

    assert client.post(f"/api/game/quiz/rooms/{room_id}/join", headers=hdr(B)).status_code == 200
    assert client.post(f"/api/game/quiz/rooms/{room_id}/ready", headers=hdr(A)).status_code == 200
    assert client.post(f"/api/game/quiz/rooms/{room_id}/ready", headers=hdr(B)).status_code == 200

    r = client.post(f"/api/game/quiz/rooms/{room_id}/start", headers=hdr(A))
    assert r.status_code == 200, r.text
    return room_id


def answers_for(room_id, q_idx):
    """(doğru_cevap, yanlış_cevap) — testler cevabı bilerek kurgulayabilsin."""
    async def _run():
        async with _db_conn(cache.db_path, user_data=True) as db:
            cur = await db.execute(
                "SELECT correct_answer, options FROM quiz_questions WHERE room_id = ? AND question_index = ?",
                (room_id, q_idx),
            )
            row = await cur.fetchone()
        correct, options = row[0], json.loads(row[1])
        wrong = next(o for o in options if o != correct)
        return correct, wrong
    return asyncio.run(_run())


def current_question(client, room_id, uid=A):
    return client.get(f"/api/game/quiz/rooms/{room_id}", headers=hdr(uid)).json()["current_question"]


def answer(client, room_id, uid, q_idx, text):
    return client.post(
        f"/api/game/quiz/rooms/{room_id}/answer",
        json={"question_index": q_idx, "selected_answer": text},
        headers=hdr(uid),
    )


def use_double_chance(client, room_id, uid, q_idx):
    return client.post(
        f"/api/game/quiz/rooms/{room_id}/joker",
        json={"question_index": q_idx, "joker_type": "double_chance"},
        headers=hdr(uid),
    )


# ─── Temel akış ──────────────────────────────────────────────────────────────

def test_duel_starts_and_advances_when_both_answer(client):
    room_id = start_duel(client)
    correct, wrong = answers_for(room_id, 0)
    assert current_question(client, room_id) == 0

    answer(client, room_id, A, 0, correct)
    assert current_question(client, room_id) == 0, "tek cevapla ilerlememeli"
    answer(client, room_id, B, 0, wrong)
    assert current_question(client, room_id) == 1, "ikisi de cevaplayınca ilerlemeli"


def test_answer_for_wrong_question_index_rejected(client):
    room_id = start_duel(client)
    correct, _ = answers_for(room_id, 3)
    r = answer(client, room_id, A, 3, correct)
    assert r.status_code == 400


def test_cannot_answer_twice_without_joker(client):
    room_id = start_duel(client)
    correct, wrong = answers_for(room_id, 0)
    assert answer(client, room_id, A, 0, wrong).status_code == 200
    r = answer(client, room_id, A, 0, correct)
    assert r.status_code == 400
    assert "zaten cevapladın" in r.json()["detail"]


# ─── double_chance (çifte şans) yarış durumu ─────────────────────────────────

def test_double_chance_retry_survives_opponent_answering_first(client):
    """Rakip ÖNCE cevaplarsa çifte şans hakkı yanmamalı.

    Regresyon: rakip cevapladıktan sonra A yanlış cevaplayınca `both_answered`
    true oluyor ve `_check_advance_question` soruyu hemen ilerletiyordu — oysa
    A'ya `can_retry` dönmüştü. A'nın ikinci denemesi "Yanlış soru index'i" ile
    düşüyordu: joker boşa gidiyor + kullanıcıya hata gösteriliyordu.
    """
    room_id = start_duel(client)
    correct, wrong = answers_for(room_id, 0)

    assert use_double_chance(client, room_id, A, 0).status_code == 200
    answer(client, room_id, B, 0, correct)          # rakip önce cevapladı

    r = answer(client, room_id, A, 0, wrong)        # A yanlış → tekrar hakkı var
    assert r.status_code == 200
    assert r.json()["correct_answer"] is None, "tekrar hakkı varken cevap sızmamalı"

    assert current_question(client, room_id) == 0, "tekrar hakkı beklerken ilerlememeli"

    retry = answer(client, room_id, A, 0, correct)  # ikinci deneme
    assert retry.status_code == 200, f"tekrar hakkı reddedildi: {retry.text}"
    assert retry.json()["is_correct"] is True


def test_double_chance_retry_survives_opponent_answering_second(client):
    """A yanlış cevapladıktan SONRA rakip cevaplarsa da hak yanmamalı."""
    room_id = start_duel(client)
    correct, wrong = answers_for(room_id, 0)

    use_double_chance(client, room_id, A, 0)
    answer(client, room_id, A, 0, wrong)            # A önce, tekrar hakkı açık
    answer(client, room_id, B, 0, correct)          # rakip sonra cevapladı

    assert current_question(client, room_id) == 0
    retry = answer(client, room_id, A, 0, correct)
    assert retry.status_code == 200, f"tekrar hakkı reddedildi: {retry.text}"


def test_double_chance_retry_survives_polling(client):
    """Bekleyen tekrar hakkı, rakibin poll'leriyle de tüketilmemeli.

    poll_room her çağrıda _check_advance_question tetikler; düzeltme yalnız
    submit_answer'a konsaydı poll yolu soruyu yine ilerletirdi.
    """
    room_id = start_duel(client)
    correct, wrong = answers_for(room_id, 0)

    use_double_chance(client, room_id, A, 0)
    answer(client, room_id, B, 0, correct)
    answer(client, room_id, A, 0, wrong)

    for _ in range(5):
        client.get(f"/api/game/quiz/rooms/{room_id}", headers=hdr(B))
    assert current_question(client, room_id) == 0

    assert answer(client, room_id, A, 0, correct).status_code == 200


def test_game_advances_after_retry_is_used(client):
    """Tekrar hakkı kullanılınca oyun DERHAL ilerlemeli (takılıp kalmamalı)."""
    room_id = start_duel(client)
    correct, wrong = answers_for(room_id, 0)

    use_double_chance(client, room_id, A, 0)
    answer(client, room_id, B, 0, correct)
    answer(client, room_id, A, 0, wrong)
    answer(client, room_id, A, 0, correct)          # tekrar tüketildi

    assert current_question(client, room_id) == 1, "tekrar sonrası ilerlemeli"


def test_second_retry_rejected(client):
    """Çifte şans yalnız BİR ek deneme verir."""
    room_id = start_duel(client)
    correct, wrong = answers_for(room_id, 0)

    use_double_chance(client, room_id, A, 0)
    answer(client, room_id, A, 0, wrong)
    answer(client, room_id, A, 0, wrong)            # tekrar da yanlış
    r = answer(client, room_id, A, 0, correct)
    assert r.status_code == 400


def test_game_advances_when_retry_never_comes(client):
    """EN KRİTİK GÜVENLİK: oyuncu tekrar denemezse oyun süre dolunca ilerlemeli.

    Kilitlenme, tek bir joker bozukluğundan çok daha kötüdür: yanlış yazılmış
    bir bekleme durumu TÜM düelloları dondururdu.
    """
    room_id = start_duel(client)
    correct, wrong = answers_for(room_id, 0)

    use_double_chance(client, room_id, A, 0)
    answer(client, room_id, B, 0, correct)
    answer(client, room_id, A, 0, wrong)            # tekrar hakkı açık kaldı
    assert current_question(client, room_id) == 0

    # Soru zamanını geriye al → süre dolmuş say
    async def _expire():
        async with _db_conn(cache.db_path, user_data=True) as db:
            await db.execute(
                "UPDATE quiz_rooms SET question_started_at = datetime('now', '-5 minutes') WHERE id = ?",
                (room_id,),
            )
            await db.commit()
    asyncio.run(_expire())

    assert current_question(client, room_id) == 1, "süre dolunca ilerlemeli — oyun kilitlenemez"


def test_pending_retry_does_not_leak_to_next_question(client):
    """Bir sorudaki bekleme durumu sonraki soruyu bloklamamalı."""
    room_id = start_duel(client)
    c0, w0 = answers_for(room_id, 0)

    use_double_chance(client, room_id, A, 0)
    answer(client, room_id, B, 0, c0)
    answer(client, room_id, A, 0, w0)
    answer(client, room_id, A, 0, c0)
    assert current_question(client, room_id) == 1

    c1, w1 = answers_for(room_id, 1)
    answer(client, room_id, A, 1, c1)
    answer(client, room_id, B, 1, w1)
    assert current_question(client, room_id) == 2, "sonraki soru normal ilerlemeli"


def test_double_chance_only_helps_its_own_question(client):
    """Joker q0 için alındıysa q1'de ikinci deneme hakkı vermemeli."""
    room_id = start_duel(client)
    c0, w0 = answers_for(room_id, 0)
    use_double_chance(client, room_id, A, 0)
    answer(client, room_id, A, 0, c0)
    answer(client, room_id, B, 0, w0)
    assert current_question(client, room_id) == 1

    c1, w1 = answers_for(room_id, 1)
    answer(client, room_id, A, 1, w1)
    assert answer(client, room_id, A, 1, c1).status_code == 400


# ─── Joker girdisi doğrulama ─────────────────────────────────────────────────

def test_invalid_joker_type_rejected(client):
    """joker_type serbest metindi: istemci `player_jokers` JSON'una istediği
    anahtarı yazabiliyordu — iç durum anahtarlarının üzerine yazmak dahil."""
    room_id = start_duel(client)
    r = client.post(
        f"/api/game/quiz/rooms/{room_id}/joker",
        json={"question_index": 0, "joker_type": "_dc_pending"},
        headers=hdr(A),
    )
    assert r.status_code == 400
    assert "Geçersiz joker" in r.json()["detail"]


def test_same_joker_cannot_be_used_twice(client):
    room_id = start_duel(client)
    assert use_double_chance(client, room_id, A, 0).status_code == 200
    assert use_double_chance(client, room_id, A, 0).status_code == 400


def test_joker_requires_room_membership(client):
    """Odada olmayan üçüncü kişi joker kullanamamalı."""
    room_id = start_duel(client)
    async def _third():
        async with _db_conn(cache.db_path, user_data=True) as db:
            await db.execute(
                "INSERT INTO users (google_id, email, name, username, picture) VALUES (?,?,?,?,?)",
                ("g3", "c@c.com", "Cem", "cem", ""),
            )
            await db.commit()
    asyncio.run(_third())
    r = client.post(
        f"/api/game/quiz/rooms/{room_id}/joker",
        json={"question_index": 0, "joker_type": "fifty_fifty"},
        headers=hdr(3),
    )
    assert r.status_code == 403
