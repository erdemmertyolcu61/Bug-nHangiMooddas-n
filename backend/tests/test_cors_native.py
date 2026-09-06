"""Native (Capacitor) origin'leri icin CORS regresyon testleri.

Capacitor uygulamayi platforma gore FARKLI bir origin'den servis eder:
  iOS     -> capacitor://localhost
  Android -> https://localhost   (capacitor.config.ts: androidScheme: 'https')

https://localhost varsayilan listede yoktu; Android uygulamasinin tum API
cagrilari CORS preflight'inda sessizce dusuyordu.
"""
import pytest

from backend.config import ALLOWED_ORIGINS

NATIVE_ORIGINS = ["capacitor://localhost", "https://localhost", "http://localhost"]


@pytest.mark.parametrize("origin", NATIVE_ORIGINS)
def test_native_origin_allowed(origin):
    assert origin in ALLOWED_ORIGINS, (
        f"{origin} ALLOWED_ORIGINS'te yok — bu platformda tum API cagrilari CORS'a takilir"
    )


def test_no_wildcard_origin():
    """allow_credentials=True ile '*' birlesirse her site kimlikli istek atabilir."""
    assert "*" not in ALLOWED_ORIGINS


def test_web_origin_still_allowed():
    assert "https://bug-n-hangi-mooddas-n.vercel.app" in ALLOWED_ORIGINS


def test_preflight_matches_config():
    """Uctan uca: yapilandirmadaki her origin gercek preflight'ta da gecmeli."""
    from fastapi.testclient import TestClient
    import backend.main as m

    with TestClient(m.app) as c:
        for origin in NATIVE_ORIGINS:
            r = c.options(
                "/api/watchlist",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "authorization",
                },
            )
            assert r.headers.get("access-control-allow-origin") == origin, origin

        # Bilinmeyen origin hala reddedilmeli
        r = c.options(
            "/api/watchlist",
            headers={
                "Origin": "https://kotu-site.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.headers.get("access-control-allow-origin") is None
