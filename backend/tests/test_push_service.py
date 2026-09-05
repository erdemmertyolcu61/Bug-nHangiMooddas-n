"""Push bildirim katmanı regresyon testleri.

Buradaki testlerin hepsi lansman öncesi bulunan gerçek hataları kilitler:
kanal seçimi (VAPID/FCM), gece sessiz saatleri ve bildirim saati tercihinin
kalıcılığı. Ağa hiç çıkılmaz — gönderim fonksiyonları monkeypatch'lenir.
"""
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

import backend.services.push_service as ps
from backend.database import cache, _get_connection as _db_conn


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture()
def db(tmp_path, monkeypatch):
    """Temiz şemalı geçici DB (Turso kapalı, havuz kapalı)."""
    db_path = str(tmp_path / "test_push.db")
    monkeypatch.setattr(cache, "db_path", db_path)
    import backend.database as dbmod
    monkeypatch.setattr(dbmod, "_turso_client", None)
    monkeypatch.setattr(dbmod, "_pool_init", False)
    asyncio.run(cache.init_db())

    async def _seed():
        async with _db_conn(db_path, user_data=True) as conn:
            await conn.execute(
                "INSERT INTO users (google_id, email, name, username, picture) VALUES (?,?,?,?,?)",
                ("g1", "a@a.com", "Ali", "ali", ""),
            )
            await conn.commit()
    asyncio.run(_seed())
    return db_path


@pytest.fixture()
def spy(monkeypatch):
    """Gerçek gönderimi durdurup hangi kanalın çağrıldığını kaydeder."""
    calls = {"web": [], "fcm": []}

    def fake_web(sub, payload):
        calls["web"].append(sub["endpoint"])
        return "ok"

    def fake_fcm(token, payload):
        calls["fcm"].append(token)
        return "ok"

    monkeypatch.setattr(ps, "_send_web_push", fake_web)
    monkeypatch.setattr(ps, "_send_fcm_push", fake_fcm)
    return calls


# ─── Kanal seçimi ────────────────────────────────────────────────────────────

def test_fcm_subscriber_reached_when_vapid_disabled(db, spy, monkeypatch):
    """VAPID kapalıyken native (FCM) aboneye bildirim GİTMELİ.

    Regresyon: zamanlayıcı tüm planlı push'ları PUSH_ENABLED (=VAPID) bayrağına
    bağlıyordu; VAPID'siz üretimde native uygulamanın tüm bildirimleri sessizce
    ölüyordu.
    """
    monkeypatch.setattr(ps, "PUSH_ENABLED", False)

    async def run():
        await cache.save_push_subscription(1, "fcm-token-1", "", "", sub_type="fcm")
        return await ps.send_push_to_user(1, "Başlık", "Gövde")

    sent = asyncio.run(run())
    assert sent == 1
    assert spy["fcm"] == ["fcm-token-1"]
    assert spy["web"] == []


def test_vapid_subscriber_skipped_when_vapid_disabled(db, spy, monkeypatch):
    """VAPID kapalıyken web abonesine gönderim DENENMEZ (abonelik de silinmez)."""
    monkeypatch.setattr(ps, "PUSH_ENABLED", False)

    async def run():
        await cache.save_push_subscription(1, "https://web.push/ep1", "p256", "auth")
        sent = await ps.send_push_to_user(1, "Başlık", "Gövde")
        remaining = await cache.get_push_subscriptions(1)
        return sent, remaining

    sent, remaining = asyncio.run(run())
    assert sent == 0
    assert spy["web"] == []
    assert len(remaining) == 1, "geçici hata aboneliği silmemeli"


def test_inactive_user_push_uses_fcm_channel(db, spy, monkeypatch):
    """Re-engagement push'u native aboneye FCM'den gitmeli.

    Regresyon: main.py doğrudan _send_web_push çağırıyor ve sorgu sub_type
    seçmiyordu → FCM aboneleri boş p256dh/auth ile web push denemesine düşüp
    her seferinde başarısız oluyordu.
    """
    monkeypatch.setattr(ps, "PUSH_ENABLED", False)
    # Sessiz saat koruması testi saate bağlı kılmasın (gece koşulunca kırılırdı).
    monkeypatch.setattr(ps, "in_quiet_hours", lambda now=None: False)

    async def run():
        await cache.save_push_subscription(1, "fcm-token-2", "", "", sub_type="fcm")
        async with _db_conn(cache.db_path, user_data=True) as conn:
            await conn.execute(
                "UPDATE users SET last_active = datetime('now', '-30 days') WHERE id = 1"
            )
            await conn.commit()
        return await ps.send_push_to_inactive(7, "Sinemood", "Seni özledik")

    sent = asyncio.run(run())
    assert sent == 1
    assert spy["fcm"] == ["fcm-token-2"]


def test_gone_subscription_deleted_but_failed_kept(db, monkeypatch):
    """404/410 → abonelik silinir; geçici hata → korunur."""
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)
    results = iter(["gone", "fail"])
    monkeypatch.setattr(ps, "_send_web_push", lambda sub, payload: next(results))

    async def run():
        await cache.save_push_subscription(1, "https://web.push/gone", "p", "a")
        await cache.save_push_subscription(1, "https://web.push/keep", "p", "a")
        await ps.send_push_to_user(1, "T", "B")
        return {s["endpoint"] for s in await cache.get_push_subscriptions(1)}

    remaining = asyncio.run(run())
    assert remaining == {"https://web.push/keep"}


# ─── Sessiz saatler ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("hour,quiet", [(0, True), (3, True), (7, True), (8, False), (18, False), (23, False)])
def test_quiet_hours_window(hour, quiet):
    """Ayarlardaki saat seçici 08:00–23:00 sunuyor; gece aralığı buna uymalı."""
    now = datetime(2026, 1, 1, hour, 0, tzinfo=ZoneInfo("Europe/Istanbul"))
    assert ps.in_quiet_hours(now) is quiet


def test_broadcast_blocked_during_quiet_hours(db, spy, monkeypatch):
    """Gece 00:00–08:00 arasında broadcast gönderilmez.

    Regresyon: Mood Kâhini duyurusu gece yarısı 00:00'da HERKESE gidiyordu ve
    kullanıcının seçtiği bildirim saatini hiç okumuyordu.
    """
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)
    monkeypatch.setattr(ps, "in_quiet_hours", lambda now=None: True)

    async def run():
        await cache.save_push_subscription(1, "https://web.push/ep", "p", "a")
        return await ps.send_push_broadcast("T", "B")

    assert asyncio.run(run()) == 0
    assert spy["web"] == []


def test_broadcast_allowed_outside_quiet_hours(db, spy, monkeypatch):
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)
    monkeypatch.setattr(ps, "in_quiet_hours", lambda now=None: False)

    async def run():
        await cache.save_push_subscription(1, "https://web.push/ep", "p", "a")
        return await ps.send_push_broadcast("T", "B")

    assert asyncio.run(run()) == 1


# ─── Bildirim saati tercihi ──────────────────────────────────────────────────

def test_second_device_inherits_notify_hour(db):
    """İkinci cihaz kullanıcının seçtiği saati devralmalı.

    Regresyon: INSERT notify_hour'ı sabit 18 yazıyordu → iki cihazı olan
    kullanıcı günün filmi bildirimini iki farklı saatte iki kez alıyordu.
    """
    async def run():
        await cache.save_push_subscription(1, "ep-phone", "p", "a")
        await cache.set_notify_hour(1, 9)
        await cache.save_push_subscription(1, "ep-tablet", "p", "a")
        async with _db_conn(cache.db_path, user_data=True) as conn:
            cur = await conn.execute(
                "SELECT DISTINCT notify_hour FROM push_subscriptions WHERE user_id = 1"
            )
            return [r[0] for r in await cur.fetchall()]

    assert asyncio.run(run()) == [9]


def test_set_notify_hour_reports_failure_without_subscription(db):
    """Aboneliği olmayan kullanıcıya 'kaydedildi' denmemeli."""
    async def run():
        stored = await cache.set_notify_hour(1, 9)
        await cache.save_push_subscription(1, "ep", "p", "a")
        return stored, await cache.set_notify_hour(1, 9)

    without_sub, with_sub = asyncio.run(run())
    assert without_sub is False
    assert with_sub is True


def test_hourly_push_matches_only_chosen_hour(db, spy, monkeypatch):
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)

    async def run():
        await cache.save_push_subscription(1, "ep", "p", "a")
        await cache.set_notify_hour(1, 9)
        at_nine = await ps.send_push_for_hour(9, "T", "B")
        at_eighteen = await ps.send_push_for_hour(18, "T", "B")
        return at_nine, at_eighteen

    at_nine, at_eighteen = asyncio.run(run())
    assert (at_nine, at_eighteen) == (1, 0)


# ─── Kategori bazlı kapatma ──────────────────────────────────────────────────

def test_categories_have_matching_columns(db):
    """NOTIFY_CATEGORIES ile şema kolonları ayrışmamalı."""
    from backend.database import NOTIFY_CATEGORIES

    async def run():
        async with _db_conn(cache.db_path, user_data=True) as conn:
            cur = await conn.execute("PRAGMA table_info(push_subscriptions)")
            return {r[1] for r in await cur.fetchall()}

    cols = asyncio.run(run())
    for cat in NOTIFY_CATEGORIES:
        assert f"notify_{cat}" in cols, f"notify_{cat} kolonu yok"


def test_unknown_category_rejected():
    """Kategori adı SQL'e gömülüyor — beyaz liste dışı değer hata vermeli."""
    from backend.database import _notify_column
    with pytest.raises(ValueError):
        _notify_column("game; DROP TABLE push_subscriptions")


def test_defaults_are_all_on(db):
    """Yeni abone hiçbir bildirimi kaçırmamalı (mevcut davranış korunur)."""
    async def run():
        await cache.save_push_subscription(1, "ep", "p", "a")
        return await cache.get_notify_prefs(1)

    assert asyncio.run(run()) == {"social": True, "daily": True, "game": True, "digest": True}


def test_disabled_category_is_not_delivered(db, spy, monkeypatch):
    """Kapatılan kategori gönderilmez, açık olan gönderilir."""
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)
    monkeypatch.setattr(ps, "in_quiet_hours", lambda now=None: False)

    async def run():
        await cache.save_push_subscription(1, "ep", "p", "a")
        await cache.set_notify_prefs(1, {"game": False})
        game = await ps.send_push_broadcast("T", "B", category="game")
        digest = await ps.send_push_broadcast("T", "B", category="digest")
        return game, digest

    game, digest = asyncio.run(run())
    assert game == 0, "kapatılan kategori gönderildi"
    assert digest == 1, "kapatılmayan kategori engellendi"


def test_disabling_marketing_keeps_transactional(db, spy, monkeypatch):
    """Pazarlama kapatılınca arkadaşlık/öneri bildirimi çalışmaya devam etmeli."""
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)

    async def run():
        await cache.save_push_subscription(1, "ep", "p", "a")
        await cache.set_notify_prefs(1, {"game": False, "digest": False, "daily": False})
        return await ps.send_push_to_user(1, "T", "B")  # category="social"

    assert asyncio.run(run()) == 1


def test_disabled_daily_excluded_from_hourly_push(db, spy, monkeypatch):
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)

    async def run():
        await cache.save_push_subscription(1, "ep", "p", "a")
        await cache.set_notify_hour(1, 9)
        before = await ps.send_push_for_hour(9, "T", "B")
        await cache.set_notify_prefs(1, {"daily": False})
        after = await ps.send_push_for_hour(9, "T", "B")
        return before, after

    assert asyncio.run(run()) == (1, 0)


def test_disabled_digest_excluded_from_reengagement(db, spy, monkeypatch):
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)
    monkeypatch.setattr(ps, "in_quiet_hours", lambda now=None: False)

    async def run():
        await cache.save_push_subscription(1, "ep", "p", "a")
        await cache.set_notify_prefs(1, {"digest": False})
        async with _db_conn(cache.db_path, user_data=True) as conn:
            await conn.execute("UPDATE users SET last_active = datetime('now', '-30 days') WHERE id = 1")
            await conn.commit()
        return await ps.send_push_to_inactive(7, "T", "B")

    assert asyncio.run(run()) == 0


def test_second_device_inherits_category_prefs(db):
    """Kapatılan kategori ikinci cihazda sessizce geri açılmamalı."""
    async def run():
        await cache.save_push_subscription(1, "ep-phone", "p", "a")
        await cache.set_notify_prefs(1, {"digest": False})
        await cache.save_push_subscription(1, "ep-tablet", "p", "a")
        async with _db_conn(cache.db_path, user_data=True) as conn:
            cur = await conn.execute(
                "SELECT DISTINCT notify_digest FROM push_subscriptions WHERE user_id = 1")
            return [r[0] for r in await cur.fetchall()]

    assert asyncio.run(run()) == [0]


def test_set_prefs_reports_failure_without_subscription(db):
    async def run():
        return await cache.set_notify_prefs(1, {"game": False})

    assert asyncio.run(run()) is False


def test_null_prefs_treated_as_enabled(db, spy, monkeypatch):
    """Geri-doldurulmamış eski satır (NULL) 'kapalı' sanılıp bildirimi kesmemeli."""
    monkeypatch.setattr(ps, "PUSH_ENABLED", True)
    monkeypatch.setattr(ps, "in_quiet_hours", lambda now=None: False)

    async def run():
        await cache.save_push_subscription(1, "ep", "p", "a")
        async with _db_conn(cache.db_path, user_data=True) as conn:
            await conn.execute("UPDATE push_subscriptions SET notify_game = NULL")
            await conn.commit()
        prefs = await cache.get_notify_prefs(1)
        sent = await ps.send_push_broadcast("T", "B", category="game")
        return prefs["game"], sent

    assert asyncio.run(run()) == (True, 1)


# ─── /api/push/preferences uçları ────────────────────────────────────────────

@pytest.fixture()
def client(db):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.routers.push import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _auth(uid=1):
    from backend.auth_utils import _create_token
    return {"Authorization": f"Bearer {_create_token({'type': 'user', 'user_id': uid}, 1)}"}


def test_preferences_require_login(client):
    assert client.get("/api/push/preferences").status_code in (401, 403)
    assert client.post("/api/push/preferences", json={"game": False}).status_code in (401, 403)


def test_preferences_roundtrip(client):
    asyncio.run(cache.save_push_subscription(1, "ep", "p", "a"))
    r = client.post("/api/push/preferences", json={"game": False}, headers=_auth())
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["preferences"]["game"] is False
    # Gönderilmeyen kategoriler dokunulmadan kalmalı (kısmi güncelleme)
    assert body["preferences"]["social"] is True
    assert client.get("/api/push/preferences", headers=_auth()).json()["preferences"]["game"] is False


def test_preferences_partial_update_does_not_reset_others(client):
    asyncio.run(cache.save_push_subscription(1, "ep", "p", "a"))
    client.post("/api/push/preferences", json={"game": False}, headers=_auth())
    client.post("/api/push/preferences", json={"digest": False}, headers=_auth())
    prefs = client.get("/api/push/preferences", headers=_auth()).json()["preferences"]
    assert prefs == {"social": True, "daily": True, "game": False, "digest": False}


def test_preferences_reject_unknown_category(client):
    """Şemada olmayan alan sessizce yutulmalı, 500'e dönüşmemeli."""
    asyncio.run(cache.save_push_subscription(1, "ep", "p", "a"))
    r = client.post("/api/push/preferences", json={"bilinmeyen": False}, headers=_auth())
    assert r.status_code == 200
    assert r.json()["ok"] is False
    assert r.json()["preferences"]["social"] is True


def test_preferences_are_scoped_to_caller(client):
    """Bir kullanıcının tercihi başka kullanıcınınkini değiştirmemeli."""
    asyncio.run(cache.save_push_subscription(1, "ep", "p", "a"))
    client.post("/api/push/preferences", json={"game": False}, headers=_auth(uid=1))
    assert asyncio.run(cache.get_notify_prefs(1))["game"] is False
    assert asyncio.run(cache.get_notify_prefs(2))["game"] is True
