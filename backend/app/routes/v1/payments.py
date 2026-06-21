from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import ipaddress
from app.database import SessionLocal
from json import JSONDecodeError
from yookassa.domain.notification import WebhookNotification
from sqlalchemy import select
from app.models import Payment
from app.models.enums import PaymentStatus
from app.services import debit_funds
from loguru import logger

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
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


async def yookassa_webhook_func(payment):
    async with SessionLocal() as db:
        # Сам идентификатор платежа ЮKassa (тот самый yookassa_id)
        yookassa_id = payment.id

        if not yookassa_id:
            logger.error("Missing yookassa id")

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


@payment_router.post("/yookassa/webhook")
async def yookassa_webhook(request: Request, background_tasks: BackgroundTasks):
    client_ip = _extract_client_ip(request)

    if not check_ip(client_ip):
        raise HTTPException(403, detail="IP is not allowed")

    try:
        payload = await request.json()
    except JSONDecodeError as exc:
        raise HTTPException(400, detail=f"Bad payload. Exception - {exc}")

    try:
        notification = WebhookNotification(payload)
    except Exception:
        raise HTTPException(400, detail="Bad notification")
    background_tasks.add_task(yookassa_webhook_func, notification.object)
    return {"status": "ok"}
