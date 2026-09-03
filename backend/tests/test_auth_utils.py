"""auth_utils saf JWT yardımcıları için birim testleri (ağ/DB gerektirmez)."""
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from backend.auth_utils import _create_token, _verify_token, optional_user_id


def _request(auth_token: str | None = None) -> Request:
    """Minimal ASGI scope'undan Request üret (ağ/DB yok)."""
    headers = []
    if auth_token is not None:
        headers.append((b"authorization", f"Bearer {auth_token}".encode()))
    return Request({"type": "http", "method": "GET", "path": "/", "headers": headers})


def test_token_roundtrip_preserves_payload():
    token = _create_token({"type": "user", "user_id": 7}, expires_hours=1)
    decoded = _verify_token(token)
    assert decoded["type"] == "user"
    assert decoded["user_id"] == 7
    assert "exp" in decoded


def test_expired_token_raises_401():
    # Negatif süre → anında süresi dolmuş token
    token = _create_token({"type": "user", "user_id": 1}, expires_hours=-1)
    with pytest.raises(HTTPException) as exc:
        _verify_token(token)
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()


def test_garbage_token_raises_401():
    with pytest.raises(HTTPException) as exc:
        _verify_token("not.a.real.jwt")
    assert exc.value.status_code == 401


# ─── optional_user_id: misafir sentinel'i ───────────────────────────────────
# Regresyon koruması: bu fonksiyon anonim ziyaretçide 0 döner, None DEĞİL.
# Uçlarda "if uid is None" yazıldığında koruma hiç tetiklenmez ve tüm misafirler
# sunucuda ortak user_id=0 kovasını paylaşır (izleme listesi/not sızıntısı).
# Misafir kontrolü daima falsy testiyle ("if not uid") yapılmalıdır.

def test_optional_user_id_returns_zero_not_none_for_anonymous():
    uid = optional_user_id(_request())
    assert uid == 0
    assert uid is not None, "Misafir sentinel'i None olursa 'if not uid' korumaları gözden geçirilmeli"
    assert not uid


def test_optional_user_id_returns_zero_for_invalid_token():
    # Bozuk token sessizce misafir sayılır (401 fırlatmaz)
    assert optional_user_id(_request("not.a.real.jwt")) == 0


def test_optional_user_id_returns_user_id_for_valid_token():
    token = _create_token({"type": "user", "user_id": 42}, expires_hours=1)
    assert optional_user_id(_request(token)) == 42
