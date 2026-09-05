"""
Web Push (VAPID) gönderim servisi.

VAPID anahtarları yapılandırılmamışsa tüm fonksiyonlar sessizce no-op çalışır;
böylece özellik kapalıyken hiçbir akış bozulmaz. Hem HTTP uçları (main.py) hem de
sosyal tetikleyiciler (routers/social.py) buradan gönderim yapar — döngüsel import yok.
"""
import os
import json
import asyncio
import logging

from backend.config import VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, VAPID_SUBJECT
from backend.database import cache

logger = logging.getLogger(__name__)

# VAPID = tarayıcı (web push) kanalı. Native uygulama FCM kullanır ve VAPID'e
# hiç ihtiyaç duymaz — bu yüzden iki kanal AYRI bayraklarla temsil edilir.
PUSH_ENABLED = bool(VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY)

# Firebase Admin SDK, kimlik bilgisini bu standart env'lerden okur
# (GOOGLE_APPLICATION_CREDENTIALS = servis hesabı JSON yolu, FIREBASE_CONFIG =
# gömülü JSON). İkisi de yoksa initialize_app() kimlik bulamaz → FCM kapalıdır.
FCM_ENABLED = bool(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_CONFIG")
)

# Zamanlayıcı/admin uçlarının "push tamamen kapalı mı?" kontrolü için.
# Yalnız PUSH_ENABLED'a bakmak, VAPID'siz ama FCM'li bir kurulumda (native
# uygulama) TÜM planlı bildirimleri sessizce iptal ederdi.
PUSH_ANY_ENABLED = PUSH_ENABLED or FCM_ENABLED

# ─── Sessiz saatler ───────────────────────────────────────────────────────
# Ayarlardaki "Günlük Film Saati" seçicisi yalnız 08:00–23:00 sunuyor; yani
# ürün kullanıcıya gece bildirim göndermeyeceğini zaten taahhüt ediyor.
# Herkese giden (broadcast) bildirimler kullanıcının saatini hiç okumadığı
# için bu taahhüdü tek başına çiğneyebiliyordu — burada merkezî olarak kapatılır.
QUIET_HOURS_START = 0   # dahil
QUIET_HOURS_END = 8     # hariç
_TZ_NAME = "Europe/Istanbul"


def in_quiet_hours(now=None) -> bool:
    """Şu an (Türkiye saati) gece sessiz aralığında mıyız?"""
    if now is None:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(_TZ_NAME))
    return QUIET_HOURS_START <= now.hour < QUIET_HOURS_END


def _send_web_push(sub: dict, payload: dict) -> str:
    """Tek bir aboneliğe push gönderir.
    Döner:
      "ok"   → gönderildi
      "gone" → abonelik kalıcı geçersiz (404/410) → çağıran SİLMELİ
      "fail" → geçici/diğer hata (timeout, 429, 5xx, ağ) → abonelik KORUNMALI
    """
    if not PUSH_ENABLED:
        return "fail"
    try:
        from pywebpush import webpush, WebPushException
    except Exception:
        logger.warning("[Push] pywebpush kurulu değil — bildirim atlanıyor")
        return "fail"
    try:
        webpush(
            subscription_info={
                "endpoint": sub["endpoint"],
                "keys": {"p256dh": sub["p256dh"], "auth": sub["auth"]},
            },
            data=json.dumps(payload, ensure_ascii=False),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
            ttl=86400,
        )
        return "ok"
    except WebPushException as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status in (404, 410):
            return "gone"  # abonelik gerçekten geçersiz → çağıran temizler
        # Diğer durumlar (401/403/429/5xx vb.) geçici olabilir → aboneliği SİLME
        logger.warning("[Push] gönderim hatası (abonelik korunuyor): status=%s %s", status, e)
        return "fail"
    except Exception as e:
        logger.warning("[Push] beklenmeyen hata (abonelik korunuyor): %s", e)
        return "fail"


def _send_fcm_push(fcm_token: str, payload: dict) -> str:
    """FCM HTTP v1 ile tek bir cihaza push gönderir."""
    if not FCM_ENABLED:
        return "fail"
    try:
        import firebase_admin
        from firebase_admin import messaging as fcm_messaging
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        message = fcm_messaging.Message(
            token=fcm_token,
            notification=fcm_messaging.Notification(
                title=payload.get("title", "Sinemood"),
                body=payload.get("body", ""),
            ),
            data={"url": payload.get("url", "/"), "tag": payload.get("tag", "sinemood")},
        )
        fcm_messaging.send(message)
        return "ok"
    except Exception as e:
        err_str = str(e)
        if "not-registered" in err_str or "invalid-registration" in err_str:
            return "gone"
        logger.warning("[Push] FCM send error: %s", e)
        return "fail"


async def _deliver(sub: dict, payload: dict) -> str:
    """Aboneliği kendi kanalından gönderir (vapid → web push, fcm → Firebase).
    Kanal yapılandırılmamışsa "fail" döner; abonelik ASLA silinmez."""
    if (sub.get("sub_type") or "vapid") == "fcm":
        return await asyncio.to_thread(_send_fcm_push, sub["endpoint"], payload)
    if not PUSH_ENABLED:
        return "fail"
    return await asyncio.to_thread(_send_web_push, sub, payload)


async def _deliver_batch(subs: list, payload: dict, pwa_only: bool = False) -> int:
    """Abonelik listesine gönderir, yalnızca kalıcı geçersiz (404/410/UNREGISTERED)
    olanları temizler. Döner: başarıyla gönderilen cihaz sayısı."""
    sent = 0
    for sub in subs:
        if pwa_only and not sub.get("is_pwa"):
            continue
        result = await _deliver(sub, payload)
        if result == "ok":
            sent += 1
        elif result == "gone":
            try:
                await cache.delete_push_subscription(sub["endpoint"])
            except Exception:
                pass
        # "fail": geçici hata veya kanal kapalı → aboneliği KORU (silme)
    return sent


async def send_push_to_user(user_id: int, title: str, body: str,
                            url: str = "/", tag: str = "sinemood") -> int:
    """Bir kullanıcının tüm cihazlarına push gönderir. Ölü abonelikleri temizler.
    Döner: başarıyla gönderilen cihaz sayısı."""
    if not user_id:
        return 0
    try:
        subs = await cache.get_push_subscriptions(user_id)
    except Exception:
        return 0
    payload = {"title": title, "body": body, "url": url, "tag": tag}
    return await _deliver_batch(subs, payload)


async def send_push_for_hour(hour: int, title: str, body: str, url: str = "/",
                             tag: str = "sinemood", pwa_only: bool = False) -> int:
    """notify_hour == hour olan abonelere push gönderir (kullanıcı-ayarlı günlük saat).
    pwa_only=False (varsayılan): Android tarayıcı aboneleri DAHİL herkese gönderir.
    (iOS yalnız kurulu PWA'da abone olabildiği için is_pwa filtresi gereksiz.)
    Ölü abonelikleri temizler. Döner: başarıyla gönderilen cihaz sayısı."""
    try:
        subs = await cache.get_push_subscriptions_by_hour(hour)
    except Exception:
        return 0
    payload = {"title": title, "body": body, "url": url, "tag": tag}
    return await _deliver_batch(subs, payload, pwa_only=pwa_only)


async def send_push_broadcast(title: str, body: str, url: str = "/", tag: str = "sinemood",
                              pwa_only: bool = False, allow_quiet_hours: bool = False) -> int:
    """Tüm abonelere push gönderir (günlük içerik). Ölü abonelikleri temizler.
    pwa_only=True: sadece Ana Ekrana Eklenmiş (PWA) kullanıcılara gönderir.
    Gece sessiz saatlerinde (00:00–08:00) gönderim yapılmaz; bilinçli bir
    istisna gerekiyorsa allow_quiet_hours=True geçilmeli.
    Döner: başarıyla gönderilen cihaz sayısı."""
    if not allow_quiet_hours and in_quiet_hours():
        logger.info("[Push] Sessiz saat — broadcast atlandi (tag=%s)", tag)
        return 0
    try:
        subs = await cache.get_all_push_subscriptions()
    except Exception:
        return 0
    payload = {"title": title, "body": body, "url": url, "tag": tag}
    return await _deliver_batch(subs, payload, pwa_only=pwa_only)


async def send_push_to_inactive(days: int, title: str, body: str, url: str = "/",
                                tag: str = "re-engage", allow_quiet_hours: bool = False) -> int:
    """`days` gündür uygulamaya girmemiş kullanıcılara hatırlatma push'u.
    Kanal ayrımını _deliver_batch yapar — native (FCM) aboneler de kapsanır.
    Kullanıcının istemediği bir pazarlama mesajı olduğu için broadcast ile aynı
    sessiz saat korumasına tabidir."""
    if not allow_quiet_hours and in_quiet_hours():
        logger.info("[Push] Sessiz saat — re-engagement atlandi")
        return 0
    try:
        subs = await cache.get_inactive_user_subs(days=days)
    except Exception as e:
        logger.warning("[Push] pasif kullanici sorgusu basarisiz: %s", e)
        return 0
    payload = {"title": title, "body": body, "url": url, "tag": tag}
    return await _deliver_batch(subs, payload)
