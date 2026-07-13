<<<<<<< HEAD
"""Production API Gateway. V45 Correction: TransactionType enum."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
=======
"""
AFM API Gateway — FastAPI with real payment endpoint
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal
>>>>>>> origin_afm/main
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
<<<<<<< HEAD

from config.config import get_settings
from config.database import init_db, engine
from config.exceptions import AFMException
from config.logging_config import configure_logging
from config.rate_limit import rate_limiter
from config.security import decode_token
from config.telemetry import app_info, http_requests_total, http_request_duration, get_metrics_response, CONTENT_TYPE_LATEST
from event_bus.redis_producer import event_producer
=======
import structlog

from config.config import get_settings
from config.database import init_db, get_db, engine
from config.exceptions import (
    AFMException, ValidationError, PaymentError, ConflictError, NotFoundError,
)
from config.logging_config import configure_logging
from config.security import get_current_user_id, create_access_token
from event_bus.redis_producer import event_producer
from event_bus.event_schema import BaseEvent, EventType
from payment_hub.payment_service import payment_service
from payment_hub.models import Transaction
from api_gateway.auth import router as auth_router
>>>>>>> origin_afm/main

logger = configure_logging()


<<<<<<< HEAD
class TransactionType(str, Enum):
    """V45 Correction: Enum for transaction types."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    TRADE = "trade"
    COPY_TRADE = "copy_trade"
    FEE = "fee"
    REVENUE_SPLIT = "revenue_split"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    settings = get_settings()
    app_info.info({
        "version": "prod-1.0.0",
        "environment": settings.environment,
    })
    logger.info("Starting Africa Frontier Markets API", environment=settings.environment)
    await init_db()
    yield
    logger.info("Shutting down gracefully...")
    await event_producer.close()
    await rate_limiter.close()
    await engine.dispose()
    logger.info("Shutdown complete")
=======
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    settings = get_settings()
    logger.info("Starting AFM API", environment=settings.environment)
    if settings.is_development:
        # 🟢 RENDER/PROD NOTE: create_all() is a dev convenience only. In
        # staging/production, schema changes are applied via Alembic
        # (`alembic upgrade head`, wired as the Render preDeployCommand)
        # so there's a real, reviewable migration history instead of
        # SQLAlchemy silently reconciling the schema on every boot.
        await init_db()
    yield
    logger.info("Shutting down AFM API")
    await payment_service.close()
    await event_producer.close()
    await engine.dispose()
>>>>>>> origin_afm/main


app = FastAPI(
    title="Africa Frontier Markets API",
<<<<<<< HEAD
    description="Unified API for EasyMarkets trading and FrontierPay payments",
=======
    description="B2B Fintech API for African payment corridors and US equity trading",
>>>>>>> origin_afm/main
    version="prod-1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if get_settings().is_development else None,
    redoc_url="/redoc" if get_settings().is_development else None,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

<<<<<<< HEAD
=======
app.include_router(auth_router)

>>>>>>> origin_afm/main
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Idempotency-Key"],
    max_age=600,
)


<<<<<<< HEAD
=======
# 🟠 FIX 4: Global AFMException handler — returns correct status codes
>>>>>>> origin_afm/main
@app.exception_handler(AFMException)
async def afm_exception_handler(request: Request, exc: AFMException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "detail": exc.detail},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now(timezone.utc)
    request_id = request.headers.get("X-Request-ID", "unknown")
<<<<<<< HEAD

    import structlog
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)

    response = await call_next(request)

    duration = (datetime.now(timezone.utc) - start).total_seconds()
    http_request_duration.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()

=======
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)
    response = await call_next(request)
    duration = (datetime.now(timezone.utc) - start).total_seconds()
>>>>>>> origin_afm/main
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )
<<<<<<< HEAD

=======
>>>>>>> origin_afm/main
    return response


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/ready")
async def readiness_check():
<<<<<<< HEAD
    checks = {
        "database": await _check_database(),
        "redis": await _check_redis(),
    }
    all_ready = all(checks.values())

    if not all_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": checks},
        )

    return {"status": "ready", "checks": checks}


async def _check_database() -> bool:
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def _check_redis() -> bool:
    try:
        import redis.asyncio as redis
        client = redis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        await client.close()
        return True
    except Exception:
        return False


@app.get("/metrics")
async def metrics():
    return PlainTextResponse(
        content=get_metrics_response(),
        media_type=CONTENT_TYPE_LATEST,
    )
=======
    return {"status": "ready"}
>>>>>>> origin_afm/main


@app.get("/")
async def root():
    return {
        "name": "Africa Frontier Markets",
        "version": "prod-1.0.0",
        "status": "operational",
    }


<<<<<<< HEAD
async def get_current_user(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = auth[7:]
    try:
        payload = decode_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


async def rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    await rate_limiter.is_allowed(
        f"ip:{client_ip}",
        limit=100,
        window_seconds=60,
    )
    return True


@app.get("/api/v1/wallet/balance", dependencies=[Depends(rate_limit)])
async def get_wallet_balance(user=Depends(get_current_user)):
    return {"user_id": user.get("sub"), "balances": {}}


=======
if get_settings().is_development:
    # 🔴 FIX: dev-only helper to obtain a bearer token for local testing,
    # now that /api/v1/payments requires real authentication. Never
    # mounted outside `environment=development` (see `is_development`).
    @app.post("/dev/token")
    async def issue_dev_token():
        demo_user_id = str(uuid.uuid4())
        token = create_access_token({"sub": demo_user_id})
        return {"access_token": token, "token_type": "bearer", "user_id": demo_user_id}


# ═══════════════════════════════════════════════════════════════════════════════
# PAYMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field


class PaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount in local currency")
    currency: str = Field(..., min_length=3, max_length=3, description="XOF, XAF, NGN, KES, GHS, ZAR, USD, EUR, GBP")
    method: str = Field(default="mobile_money", description="mobile_money, card, bank_transfer, ussd")
    phone_number: str | None = Field(None, description="Required for mobile_money")
    region: str = Field(default="west_africa", description="west_africa, east_africa, south_africa, central_africa, international")
    metadata: dict = Field(default_factory=dict)


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: str
    currency: str
    fee_amount: str
    net_amount: str
    psp: str
    psp_transaction_id: str | None
    created_at: str


# 🟠 FIX 4: No generic Exception catch — let AFMException propagate to handler
@app.post("/api/v1/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: Request,
    payment: PaymentRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Create a new payment — initiates REAL PSP processing.

    Flow:
    1. Authenticate caller (JWT bearer token → user UUID)
    2. Validate request
    3. Route to appropriate PSP (Kora, Fincra, Flutterwave, MTN MoMo, Orange Money)
    4. Process payment via PSP API
    5. Store transaction in DB
    6. Return result

    🔴 FIX: previously `user_id` was hardcoded to the string
    "user_demo_001", which is not a valid UUID and doesn't reference any
    row in `users`. Every real call crashed against Postgres (invalid UUID
    / FK violation) and, more importantly, was not actually authenticated.
    Now the caller must present a valid JWT (see POST /dev/token in
    development to obtain a test token).
    """
    # 🟠 FIX 5: Read X-Idempotency-Key from header if provided
    idempotency_key = request.headers.get("X-Idempotency-Key")

    logger.info(
        "Payment request received",
        user_id=str(user_id),
        amount=str(payment.amount),
        currency=payment.currency,
        method=payment.method,
    )

    # Let AFMException propagate — global handler catches it with correct status code
    transaction = await payment_service.process_payment(
        user_id=user_id,
        amount=payment.amount,
        currency=payment.currency,
        method=payment.method,
        region=payment.region,
        phone_number=payment.phone_number,
        metadata=payment.metadata,
        idempotency_key=idempotency_key,  # 🟠 FIX 5: Pass through
    )

    # Emit event for async processing
    event = BaseEvent(
        event_type=EventType.PAYMENT_COMPLETED if transaction.status.value == "completed" else EventType.PAYMENT_FAILED,
        payload={
            "transaction_id": str(transaction.id),
            "user_id": str(transaction.user_id),
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status.value,
            "psp": transaction.psp.value,
        },
    )
    await event_producer.publish(event)

    return PaymentResponse(
        transaction_id=str(transaction.id),
        status=transaction.status.value,
        amount=str(transaction.amount),
        currency=transaction.currency,
        fee_amount=str(transaction.fee_amount),
        net_amount=str(transaction.net_amount),
        psp=transaction.psp.value,
        psp_transaction_id=transaction.psp_transaction_id,
        created_at=transaction.created_at.isoformat(),
    )


@app.get("/api/v1/payments/{transaction_id}")
async def get_payment(
    transaction_id: str,
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Get payment by ID.

    🔴 FIX: transaction_id is now validated as a UUID before hitting the
    DB (an invalid value used to bubble up as a raw, unhandled DB error
    instead of a clean 404/422), and the transaction is scoped to the
    authenticated caller so users can't read each other's payments.
    """
    try:
        parsed_id = uuid.UUID(transaction_id)
    except ValueError:
        raise ValidationError(f"'{transaction_id}' is not a valid transaction id")

    transaction = await payment_service.get_transaction(parsed_id)

    if transaction.user_id != user_id:
        # Same response as "not found" to avoid leaking existence of other users' txns
        raise NotFoundError(f"Transaction {transaction_id} not found")

    return {
        "transaction_id": str(transaction.id),
        "status": transaction.status.value,
        "amount": str(transaction.amount),
        "currency": transaction.currency,
        "psp": transaction.psp.value,
        "psp_transaction_id": transaction.psp_transaction_id,
        "psp_response": transaction.psp_response,
        "created_at": transaction.created_at.isoformat(),
        "updated_at": transaction.updated_at.isoformat(),
    }


# Webhook endpoints with HMAC verification
>>>>>>> origin_afm/main
@app.post("/webhooks/kora")
async def kora_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Kora-Signature", "")

<<<<<<< HEAD
    from payment_hub.payment_service import payment_service
=======
>>>>>>> origin_afm/main
    if not await payment_service.verify_webhook("kora", payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()
    logger.info("Kora webhook received", event=data.get("event"))
    return {"status": "received"}


@app.post("/webhooks/fincra")
async def fincra_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Fincra-Signature", "")

<<<<<<< HEAD
    from payment_hub.payment_service import payment_service
=======
>>>>>>> origin_afm/main
    if not await payment_service.verify_webhook("fincra", payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()
    logger.info("Fincra webhook received", event=data.get("event"))
    return {"status": "received"}


<<<<<<< HEAD
@app.post("/platforms")
async def onboard_platform(request: Request):
    from platform_manager.platform_service import platform_service
    data = await request.json()
    result = await platform_service.onboard_platform(
        name=data["name"],
        contact_email=data["contact_email"],
        webhook_url=data.get("webhook_url"),
    )
    return result


@app.post("/platforms/{platform_id}/rotate-key")
async def rotate_api_key(platform_id: str, user=Depends(get_current_user)):
    from platform_manager.platform_service import platform_service
    result = await platform_service.rotate_key(platform_id)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
=======
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_gateway.main:app",
>>>>>>> origin_afm/main
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        access_log=False,
    )
