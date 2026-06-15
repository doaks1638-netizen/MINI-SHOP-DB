from fastapi import APIRouter, Request, HTTPException
import ipaddress
from app.database import DBsession
from json import JSONDecodeError
from yookassa.domain.notification import WebhookNotification
from sqlalchemy import select
from app.models import Payment
from app.models.enums import PaymentStatus
from app.services import debit_funds

payment_router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)

YANDEX_IP_LIST = [
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.156.11",
    "77.75.156.35",
    "77.75.154.128/25",
    "2a02:5180::/32",
]


def check_ip(ip: str | None) -> bool:
    if ip is None:
        return False

    try:
        addres = ipaddress.ip_address(ip)
    except Exception:
        return False

    for mask in YANDEX_IP_LIST:
        if "/" in mask:
            if addres in ipaddress.ip_network(mask, strict=False):
                return True
        else:
            if addres == ipaddress.ip_address(mask):
                return True
    return False


def _extract_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


@payment_router.post("/yookassa/webhook")
async def yookassa_webhook(db: DBsession, request: Request):
    client_ip = _extract_client_ip(request)

    if not check_ip(client_ip):
        raise HTTPException(403, detail="IP is not allowed")

    try:
        payload = await request.json()
    except JSONDecodeError as exc:
        raise HTTPException(400, detail=f"Bad payload. Exception - {exc}")

    try:
        notification = WebhookNotification(payload)
    except Exception as exc:
        raise HTTPException(400, detail=f"Bad notification")

    payment = notification.object
    # Сам идентификатор платежа ЮKassa (тот самый yookassa_id)
    yookassa_id = payment.id

    if not yookassa_id:
        raise HTTPException(status_code=400, detail="Missing yookassa id")

    payment_db = await db.scalar(
        select(Payment).where(Payment.yookassa_id == yookassa_id)
    )
    if payment_db is None:
        return {"status": "ignored"}

    if payment.status == "succeeded":
        if payment_db.status != PaymentStatus.succeeded:
            payment_db.status = PaymentStatus.succeeded
            await debit_funds(db, payment_db.user_id, payment_db.amount)

    elif payment.status == "canceled":
        if payment_db.status != PaymentStatus.canceled:
            payment_db.status = PaymentStatus.canceled

    await db.commit()
    return {"status": "ok"}
