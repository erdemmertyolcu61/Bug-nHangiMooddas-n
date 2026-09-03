"""
Basit, bağımlılıksız in-memory rate limiter (IP + path bazlı).

main.py ve router'lar (social.py vb.) ortak kullanır → tek implementasyon.
Tek instance/proses için yeterli; yatay ölçeklemede Redis'e taşınmalı.
"""
import time
from collections import defaultdict

from fastapi import HTTPException, Request

from backend.config import RATE_LIMIT_GENERAL, RATE_LIMIT_AI

# Yazma/spam'a açık endpoint'ler için sıkı limit (dk/IP). Arkadaşlık isteği,
# öneri gönderimi, push aboneliği gibi yan-etkili çağrıları korur.
RATE_LIMIT_STRICT = 20

_rate_store: dict[str, list[float]] = defaultdict(list)


def _client_ip(request: Request) -> str:
    """Gerçek istemci IP'si. Prod'da tüm trafik Vercel rewrite + Railway proxy
    üzerinden gelir; request.client.host proxy IP'sidir — tüm kullanıcılar tek
    rate-limit bütçesini paylaşır (60/dk TOPLAM!). X-Forwarded-For'un ilk
    girdisi gerçek istemcidir."""
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"


def _rate_limit_identity(request: Request) -> str:
    """Limit anahtarı. Giriş yapmış kullanıcıda user_id (imzalı JWT'den gelir →
    taklit edilemez), aksi halde IP. X-Forwarded-For istemci tarafından
    uydurulabildiği için kimliği doğrulanmış çağrılarda IP'ye güvenilmez."""
    try:
        from backend.auth_utils import optional_user_id
        uid = optional_user_id(request)
        if uid:
            return f"u{uid}"
    except Exception:
        pass
    return _client_ip(request)


def _check_rate_limit(request: Request, limit: int) -> None:
    """Dakikada `limit` istek (kimlik + path başına). Aşılırsa 429."""
    ident = _rate_limit_identity(request)
    now = time.time()
    window = 60  # 1 dakika
    key = f"{ident}:{request.url.path}"
    _rate_store[key] = [t for t in _rate_store[key] if now - t < window]
    if len(_rate_store[key]) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    _rate_store[key].append(now)
    # Bellek sınırı: max 50K key
    if len(_rate_store) > 50000:
        oldest = sorted(_rate_store.keys(), key=lambda k: min(_rate_store[k]) if _rate_store[k] else 0)[:10000]
        for k in oldest:
            del _rate_store[k]


def rate_limit_general(request: Request) -> None:
    _check_rate_limit(request, RATE_LIMIT_GENERAL)


def rate_limit_ai(request: Request) -> None:
    _check_rate_limit(request, RATE_LIMIT_AI)


def rate_limit_strict(request: Request) -> None:
    _check_rate_limit(request, RATE_LIMIT_STRICT)


RATE_LIMIT_IMAGE_PROXY = 120

def rate_limit_image_proxy(request: Request) -> None:
    _check_rate_limit(request, RATE_LIMIT_IMAGE_PROXY)
