"""Abonelik doğrulama — RevenueCat server-side entitlement check."""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from backend.auth_utils import verify_user
from backend.config import REVENUECAT_API_KEY, REVENUECAT_ENTITLEMENT
from backend.services.rate_limit import rate_limit_general

logger = logging.getLogger("film_elestirimeni")
router = APIRouter(prefix="/api", tags=["subscription"])

RC_ENABLED = bool(REVENUECAT_API_KEY)


def _parse_rc_date(value: str):
    """RevenueCat ISO-8601 tarihini (…Z) timezone-aware datetime'a çevirir."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _entitlement_active(ent: dict) -> bool:
    """Entitlement şu an geçerli mi?

    RevenueCat, süresi dolmuş entitlement'ları da `entitlements` sözlüğünde
    tutar — yalnızca anahtarın varlığına bakmak, aboneliğini bir kez almış
    herkese ömür boyu premium vermek demekti. Geçerlilik `expires_date`
    (null = kalıcı satın alma) ve varsa ödemesiz uzatma penceresi
    `grace_period_expires_date` ile belirlenir.
    """
    if not isinstance(ent, dict):
        return False
    now = datetime.now(timezone.utc)
    expires = _parse_rc_date(ent.get("expires_date"))
    if expires is None:
        # Alan yoksa/boşsa: kalıcı (lifetime) satın alma.
        return "expires_date" not in ent or ent.get("expires_date") is None
    if expires > now:
        return True
    grace = _parse_rc_date(ent.get("grace_period_expires_date"))
    return bool(grace and grace > now)


@router.get("/subscription/status", dependencies=[Depends(rate_limit_general)])
async def subscription_status(user=Depends(verify_user)):
    """Kullanıcının premium durumunu RevenueCat API'den doğrular."""
    if not RC_ENABLED:
        return {"premium": False, "enabled": False}

    user_id = str(user["user_id"])
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://api.revenuecat.com/v1/subscribers/{user_id}",
                headers={
                    "Authorization": f"Bearer {REVENUECAT_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
        if resp.status_code == 404:
            return {"premium": False, "enabled": True}
        resp.raise_for_status()
        data = resp.json()
        entitlements = data.get("subscriber", {}).get("entitlements", {}) or {}
        is_premium = _entitlement_active(entitlements.get(REVENUECAT_ENTITLEMENT))
        return {"premium": is_premium, "enabled": True}
    except Exception as e:
        logger.warning("[Subscription] RevenueCat check error: %s", e)
        return {"premium": False, "enabled": True, "error": "check_failed"}
