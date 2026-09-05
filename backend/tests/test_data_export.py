"""KVKK md. 11 veri dışa aktarım ucu testleri.

Önceki durumda "Verilerim → Dışa aktar" yalnızca izleme listesini indiriyordu;
gizlilik metni ise tüm verilere erişim hakkı vaat ediyordu.
"""
import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.auth_utils import _create_token
from backend.database import cache, _get_connection as _db_conn
from backend.routers.social import _EXPORT_TABLES, _EXPORT_TABLES_PAIRED


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_export.db")
    monkeypatch.setattr(cache, "db_path", db_path)
    import backend.database as dbmod
    monkeypatch.setattr(dbmod, "_turso_client", None)
    monkeypatch.setattr(dbmod, "_pool_init", False)
    asyncio.run(cache.init_db())

    async def _seed():
        async with _db_conn(db_path, user_data=True) as db:
            await db.execute(
                "INSERT INTO users (google_id, email, name, username, picture) VALUES (?,?,?,?,?)",
                ("g1", "a@a.com", "Ali", "ali", ""),
            )
            await db.execute(
                "INSERT INTO watchlist (tmdb_id, title, user_id) VALUES (?,?,?)", (603, "Matrix", 1)
            )
            await db.execute(
                "INSERT INTO movie_notes (tmdb_id, note_content, user_id) VALUES (?,?,?)",
                (603, "Gizli notum", 1),
            )
            await db.commit()
    asyncio.run(_seed())

    from backend.routers.social import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _auth(uid=1):
    return {"Authorization": f"Bearer {_create_token({'type': 'user', 'user_id': uid}, 1)}"}


def test_export_requires_login(client):
    assert client.get("/api/auth/export").status_code in (401, 403)


def test_export_covers_every_section(client):
    """Her bölüm sorgulanabilmeli — şema kayarsa `eksik_bolumler` dolar."""
    r = client.get("/api/auth/export", headers=_auth())
    assert r.status_code == 200
    body = r.json()
    assert body["eksik_bolumler"] == [], "dışa aktarım SQL'i şemayla uyumsuz"
    expected = {k for k, _ in _EXPORT_TABLES} | {k for k, _ in _EXPORT_TABLES_PAIRED}
    assert set(body["veriler"]) == expected


def test_export_returns_user_content(client):
    """Sadece izleme listesi değil, notlar da dönmeli (eski hatanın kilidi)."""
    body = client.get("/api/auth/export", headers=_auth()).json()["veriler"]
    assert [w["tmdb_id"] for w in body["izleme_listesi"]] == [603]
    assert body["notlar"][0]["note_content"] == "Gizli notum"
    assert body["hesap"][0]["email"] == "a@a.com"


def test_export_is_scoped_to_caller(client):
    """Başka bir kullanıcının token'ı benim verimi getirmemeli."""
    body = client.get("/api/auth/export", headers=_auth(uid=999)).json()["veriler"]
    assert body["izleme_listesi"] == []
    assert body["notlar"] == []
    assert body["hesap"] == []


def test_export_mirrors_deletion_tables():
    """Dışa aktarım ile silme aynı tablo kümesini kapsamalı.

    Silinen ama dışa aktarılmayan bir tablo, kullanıcının hiç göremediği veri
    demektir. Yeni tablo eklendiğinde bu test uyarır.
    """
    import ast
    import inspect
    import textwrap
    from backend.routers import social

    src = textwrap.dedent(inspect.getsource(social.delete_account))
    tree = ast.parse(src)

    deleted = set()
    # a) Düz metin "DELETE FROM <tablo>" içeren string sabitleri
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and "DELETE FROM" in node.value:
            # f-string'in sabit parçası "DELETE FROM " ile bitebilir (tablo adı
            # ayrı bir ifade) — o durumda (b) şıkkı yakalar.
            rest = node.value.split("DELETE FROM", 1)[1].split()
            if rest:
                deleted.add(rest[0])
    # b) `for table, col in ((...),)` döngüsündeki tablo adları (f-string ile silinir)
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Tuple):
            for elt in node.iter.elts:
                if isinstance(elt, ast.Tuple) and elt.elts:
                    first = elt.elts[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                        deleted.add(first.value)
    deleted.discard("{table}")

    exported = set()
    for _, sql in _EXPORT_TABLES + _EXPORT_TABLES_PAIRED:
        exported.add(sql.split(" FROM ", 1)[1].split()[0])

    # Kullanıcının kendi içeriği olmayan, yalnızca ilişki/temizlik amaçlı tablolar.
    not_user_content = {
        "review_likes", "challenge_responses", "mood_feedback", "list_collaborators",
        "quiz_answers", "quiz_questions", "quiz_rooms", "quiz_matchmaking_queue",
        "ugc_reports", "referrals", "feed_likes", "feed_comments", "mood_reactions",
        "users",
    }
    uncovered = deleted - exported - not_user_content
    assert not uncovered, f"silinen ama dışa aktarılmayan tablolar: {sorted(uncovered)}"
