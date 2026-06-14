"""F12 · ЮKassa integration + СБП reference.

Flow:
    1. Юзер на /support выбирает сумму → POST /api/support/create-payment
    2. Мы создаём платёж через ЮKassa API → возвращаем confirmation_url
    3. Юзер платит → ЮKassa дёргает webhook /api/webhook/yookassa
    4. Webhook проверяет, что событие 'payment.succeeded' → пишет в supporters,
       ставит is_supporter=1 для сессии.

Документация:
    https://yookassa.ru/developers/api
"""

from __future__ import annotations

import base64
import ipaddress
import json
import uuid
from typing import Any

import httpx

from .config import get_settings

YK_API = "https://api.yookassa.ru/v3"

# IP-диапазоны ЮKassa для проверки webhook (из их доков).
YK_TRUSTED_RANGES = [
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.154.128/25",
    "77.75.156.11/32",
    "77.75.156.35/32",
    "2a02:5180::/32",
]


def yk_configured() -> bool:
    s = get_settings()
    return bool(s.yookassa_shop_id and s.yookassa_secret_key)


def _auth_header() -> dict[str, str]:
    s = get_settings()
    pair = f"{s.yookassa_shop_id}:{s.yookassa_secret_key}".encode()
    return {
        "Authorization": "Basic " + base64.b64encode(pair).decode(),
        "Idempotence-Key": str(uuid.uuid4()),
        "Content-Type": "application/json",
    }


def create_payment(amount_rub: float, description: str,
                   return_url: str, session_id: str | None = None,
                   nickname: str | None = None) -> dict[str, Any]:
    """Создать платёж в ЮKassa. Возвращает {id, confirmation_url, status}."""
    if not yk_configured():
        raise RuntimeError("YooKassa not configured (set YOOKASSA_SHOP_ID + YOOKASSA_SECRET_KEY)")
    if amount_rub < 10:
        raise ValueError("min 10 RUB")

    body = {
        "amount": {"value": f"{amount_rub:.2f}", "currency": "RUB"},
        "capture": True,
        "confirmation": {"type": "redirect", "return_url": return_url},
        "description": description[:128],
        "metadata": {
            "session_id": session_id or "",
            "nickname": nickname or "",
            "source": "paideia-support",
        },
    }
    with httpx.Client(timeout=15.0) as client:
        r = client.post(f"{YK_API}/payments", headers=_auth_header(), json=body)
        r.raise_for_status()
        d = r.json()
    return {
        "id": d["id"],
        "status": d["status"],
        "confirmation_url": d["confirmation"]["confirmation_url"],
        "amount": d["amount"],
    }


def ip_is_trusted(ip: str) -> bool:
    """Проверка что webhook пришёл от ЮKassa (по IP)."""
    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for cidr in YK_TRUSTED_RANGES:
        try:
            if addr in ipaddress.ip_network(cidr):
                return True
        except ValueError:
            continue
    return False


def parse_webhook_event(payload: dict) -> dict | None:
    """Распарсить событие ЮKassa. Возвращает dict с полями или None если не успех.

    Структура webhook (документация):
        {event: "payment.succeeded", object: {id, status, amount: {value, currency},
          metadata: {session_id, nickname}, ...}}
    """
    event = payload.get("event")
    obj = payload.get("object") or {}
    if event != "payment.succeeded" or obj.get("status") != "succeeded":
        return None
    amount = obj.get("amount") or {}
    try:
        amount_rub = float(amount.get("value", 0))
    except (TypeError, ValueError):
        amount_rub = 0.0
    metadata = obj.get("metadata") or {}
    return {
        "payment_id": obj.get("id"),
        "amount_rub": amount_rub,
        "currency": amount.get("currency", "RUB"),
        "session_id": metadata.get("session_id") or None,
        "nickname": metadata.get("nickname") or None,
        "captured_at": obj.get("captured_at"),
    }


def sbp_link(amount_rub: float | None = None) -> str | None:
    """Сгенерировать СБП-ссылку (sbp:// или telephone tel: для копирования)."""
    s = get_settings()
    phone = (s.sbp_phone or "").strip()
    if not phone:
        return None
    # ЮMoney и крупные банки понимают такой формат для перевода СБП
    # Реальный SBP-deeplink требует QR от банка; здесь — просто tel:-фоллбек
    return f"tel:{phone}"


def sbp_info() -> dict[str, Any] | None:
    s = get_settings()
    if not s.sbp_phone:
        return None
    return {
        "phone": s.sbp_phone,
        "bank": s.sbp_bank_name or "СБП-совместимый банк",
        "holder": s.sbp_holder_name or "",
    }
