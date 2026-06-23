"""Abonelik doğrulama — RevenueCat server-side entitlement check."""
import logging

from fastapi import APIRouter, Depends

from backend.auth_utils import verify_user
from backend.config import REVENUECAT_API_KEY, REVENUECAT_ENTITLEMENT
from backend.services.rate_limit import rate_limit_general

logger = logging.getLogger("film_elestirimeni")
router = APIRouter(prefix="/api", tags=["subscription"])

RC_ENABLED = bool(REVENUECAT_API_KEY)


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
        entitlements = data.get("subscriber", {}).get("entitlements", {})
        is_premium = REVENUECAT_ENTITLEMENT in entitlements
        return {"premium": is_premium, "enabled": True}
    except Exception as e:
        logger.warning("[Subscription] RevenueCat check error: %s", e)
        return {"premium": False, "enabled": True, "error": "check_failed"}
