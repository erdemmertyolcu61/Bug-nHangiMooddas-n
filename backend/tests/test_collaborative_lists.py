"""Ortak liste (collaborative lists) ve mood feedback entegrasyon testleri."""
import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.auth_utils import _create_token
from backend.database import cache, _get_connection as _db_conn


@pytest.fixture()
def app_client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_collab.db")
    monkeypatch.setattr(cache, "db_path", db_path)
    import backend.database as dbmod
    monkeypatch.setattr(dbmod, "_turso_client", None)
    monkeypatch.setattr(dbmod, "_pool_init", False)

    asyncio.get_event_loop_policy().new_event_loop()
    asyncio.run(cache.init_db())

    async def _seed():
        async with _db_conn(db_path, user_data=True) as db:
            await db.execute(
                "INSERT INTO users (google_id, email, name, username, picture) VALUES (?,?,?,?,?)",
                ("g1", "a@a.com", "Ali", "ali", ""),
            )
            await db.execute(
                "INSERT INTO users (google_id, email, name, username, picture) VALUES (?,?,?,?,?)",
                ("g2", "b@b.com", "Banu", "banu", ""),
            )
            await db.execute(
                "INSERT INTO users (google_id, email, name, username, picture) VALUES (?,?,?,?,?)",
                ("g3", "c@c.com", "Can", "can", ""),
            )
            await db.commit()
    asyncio.run(_seed())

    from backend.routers.lists_user import router as lists_router
    app = FastAPI()
    app.include_router(lists_router)
    return TestClient(app)


def _auth(user_id: int) -> dict:
    token = _create_token({"type": "user", "user_id": user_id}, expires_hours=1)
    return {"Authorization": f"Bearer {token}"}


# ─── Collaborator davet akışı ───────────────────────────────────────────────

def test_invite_accept_and_edit(app_client):
    created = app_client.post("/api/custom-lists",
                              json={"name": "Ortak Film", "emoji": "🤝"}, headers=_auth(1)).json()
    lid = created["id"]

    r = app_client.post(f"/api/custom-lists/{lid}/collaborators",
                        json={"username": "banu"}, headers=_auth(1))
    assert r.status_code == 200

    collabs = app_client.get(f"/api/custom-lists/{lid}/collaborators", headers=_auth(1)).json()["collaborators"]
    assert len(collabs) == 1
    assert collabs[0]["username"] == "banu"
    assert collabs[0]["status"] == "pending"

    invites = app_client.get("/api/collab-invites", headers=_auth(2)).json()["invites"]
    assert len(invites) == 1
    assert invites[0]["list_name"] == "Ortak Film"

    r = app_client.post(f"/api/collab-invites/{lid}/respond",
                        json={"accept": True}, headers=_auth(2))
    assert r.status_code == 200

    r = app_client.post(f"/api/custom-lists/{lid}/items",
                        json={"tmdb_id": 550, "title": "Fight Club"},
                        headers=_auth(2))
    assert r.status_code == 200

    data = app_client.get(f"/api/custom-lists/{lid}", headers=_auth(2)).json()
    assert len(data["movies"]) == 1
    assert data["is_owner"] is False


def test_declined_invite_blocks_edit(app_client):
    created = app_client.post("/api/custom-lists",
                              json={"name": "Tek Kişilik"}, headers=_auth(1)).json()
    lid = created["id"]

    app_client.post(f"/api/custom-lists/{lid}/collaborators",
                    json={"username": "banu"}, headers=_auth(1))
    app_client.post(f"/api/collab-invites/{lid}/respond",
                    json={"accept": False}, headers=_auth(2))

    r = app_client.post(f"/api/custom-lists/{lid}/items",
                        json={"tmdb_id": 100, "title": "X"}, headers=_auth(2))
    assert r.status_code == 404


def test_owner_removes_collaborator(app_client):
    created = app_client.post("/api/custom-lists",
                              json={"name": "Sil Beni"}, headers=_auth(1)).json()
    lid = created["id"]

    app_client.post(f"/api/custom-lists/{lid}/collaborators",
                    json={"username": "banu"}, headers=_auth(1))
    app_client.post(f"/api/collab-invites/{lid}/respond",
                    json={"accept": True}, headers=_auth(2))

    r = app_client.delete(f"/api/custom-lists/{lid}/collaborators/2", headers=_auth(1))
    assert r.status_code == 200

    r = app_client.get(f"/api/custom-lists/{lid}", headers=_auth(2))
    assert r.status_code == 404


def test_self_leave_collab(app_client):
    created = app_client.post("/api/custom-lists",
                              json={"name": "Ayrılıyorum"}, headers=_auth(1)).json()
    lid = created["id"]

    app_client.post(f"/api/custom-lists/{lid}/collaborators",
                    json={"username": "can"}, headers=_auth(1))
    app_client.post(f"/api/collab-invites/{lid}/respond",
                    json={"accept": True}, headers=_auth(3))

    r = app_client.delete(f"/api/custom-lists/{lid}/collaborators/3", headers=_auth(3))
    assert r.status_code == 200


def test_non_owner_cannot_invite(app_client):
    created = app_client.post("/api/custom-lists",
                              json={"name": "Sadece Sahibi"}, headers=_auth(1)).json()
    lid = created["id"]

    r = app_client.post(f"/api/custom-lists/{lid}/collaborators",
                        json={"username": "can"}, headers=_auth(2))
    assert r.status_code == 400


def test_collaborated_lists_endpoint(app_client):
    created = app_client.post("/api/custom-lists",
                              json={"name": "Ortak"}, headers=_auth(1)).json()
    lid = created["id"]

    app_client.post(f"/api/custom-lists/{lid}/collaborators",
                    json={"username": "banu"}, headers=_auth(1))
    app_client.post(f"/api/collab-invites/{lid}/respond",
                    json={"accept": True}, headers=_auth(2))

    r = app_client.get("/api/collaborated-lists", headers=_auth(2))
    assert r.status_code == 200
    lists = r.json()["lists"]
    assert len(lists) == 1
    assert lists[0]["name"] == "Ortak"
    assert lists[0]["is_collab"] is True


# ─── Mood feedback ──────────────────────────────────────────────────────────

def test_mood_feedback_crud(app_client):
    r = app_client.post("/api/movies/550/mood-feedback",
                        json={"mood_id": "battaniye", "feedback": "perfect_match"},
                        headers=_auth(1))
    assert r.status_code == 200

    r = app_client.get("/api/movies/550/mood-feedback?mood_id=battaniye", headers=_auth(1))
    assert r.status_code == 200
    assert r.json()["my_feedback"] == "perfect_match"
    assert r.json()["stats"]["perfect_match"] == 1

    r = app_client.post("/api/movies/550/mood-feedback",
                        json={"mood_id": "battaniye", "feedback": "wrong_mood"},
                        headers=_auth(1))
    assert r.status_code == 200
    r = app_client.get("/api/movies/550/mood-feedback?mood_id=battaniye", headers=_auth(1))
    assert r.json()["my_feedback"] == "wrong_mood"


def test_mood_feedback_invalid_type_rejected(app_client):
    r = app_client.post("/api/movies/550/mood-feedback",
                        json={"mood_id": "battaniye", "feedback": "invalid"},
                        headers=_auth(1))
    assert r.status_code == 422


def test_mood_feedback_requires_mood_id(app_client):
    r = app_client.get("/api/movies/550/mood-feedback", headers=_auth(1))
    assert r.status_code == 422
