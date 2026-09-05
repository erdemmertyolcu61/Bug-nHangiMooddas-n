"""RevenueCat entitlement doğrulama testleri.

Regresyon: premium kontrolü `REVENUECAT_ENTITLEMENT in entitlements` şeklindeydi.
RevenueCat süresi dolmuş entitlement'ları da aynı sözlükte döndürdüğü için bir
kez abone olan herkes ömür boyu premium kalıyordu.
"""
from datetime import datetime, timedelta, timezone

import pytest

from backend.routers.subscription import _entitlement_active, _parse_rc_date


def _iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


NOW = datetime.now(timezone.utc)


def test_future_expiry_is_active():
    assert _entitlement_active({"expires_date": _iso(NOW + timedelta(days=10))}) is True


def test_past_expiry_is_not_active():
    assert _entitlement_active({"expires_date": _iso(NOW - timedelta(days=1))}) is False


def test_lifetime_purchase_is_active():
    """expires_date null = kalıcı (lifetime) satın alma."""
    assert _entitlement_active({"expires_date": None}) is True


def test_expired_but_in_grace_period_is_active():
    """Ödeme sorunu penceresinde kullanıcı erişimini kaybetmemeli."""
    ent = {
        "expires_date": _iso(NOW - timedelta(days=1)),
        "grace_period_expires_date": _iso(NOW + timedelta(days=3)),
    }
    assert _entitlement_active(ent) is True


def test_expired_with_expired_grace_is_not_active():
    ent = {
        "expires_date": _iso(NOW - timedelta(days=10)),
        "grace_period_expires_date": _iso(NOW - timedelta(days=3)),
    }
    assert _entitlement_active(ent) is False


def test_missing_entitlement_is_not_active():
    """Sözlükte hiç yoksa (.get → None) premium verilmemeli."""
    assert _entitlement_active(None) is False


@pytest.mark.parametrize("bad", ["", "not-a-date", "2026-13-45"])
def test_unparseable_expiry_is_not_active(bad):
    """Bozuk tarih 'kalıcı satın alma' sayılmamalı — fail-closed."""
    assert _entitlement_active({"expires_date": bad}) is False


def test_parse_rc_date_handles_z_suffix():
    parsed = _parse_rc_date("2026-01-01T00:00:00Z")
    assert parsed == datetime(2026, 1, 1, tzinfo=timezone.utc)
