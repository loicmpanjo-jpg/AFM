"""
AFM Event Worker — consumes `afm:events` and reacts to payment/trade events.

🔴 FIX: README claimed "Worker with pass/TODO -> Real event handling" as
already done, but no worker file existed anywhere in the repo — the Redis
Streams consumer (event_bus/redis_consumer.py) was fully implemented but
never actually instantiated or run by anything. This file wires it up with
a real (if intentionally minimal) handler per event type, and gives you a
concrete place to add the domain logic that was previously a documentation
promise with nothing behind it.

Run with:
    python -m event_bus.worker
"""

import asyncio

from config.logging_config import configure_logging
from event_bus.event_schema import EventType
from event_bus.redis_consumer import EventConsumer

logger = configure_logging()


async def handle_event(data: dict) -> None:
    event_type = data.get("event_type")
    payload = data.get("payload", {})

    if event_type == EventType.PAYMENT_COMPLETED.value:
        logger.info(
            "Payment completed — ready for settlement",
            transaction_id=payload.get("transaction_id"),
            amount=payload.get("amount"),
            currency=payload.get("currency"),
        )
        # TODO(business logic): enqueue settlement batch, notify merchant, etc.

    elif event_type == EventType.PAYMENT_FAILED.value:
        logger.warning(
            "Payment failed",
            transaction_id=payload.get("transaction_id"),
            currency=payload.get("currency"),
        )
        # TODO(business logic): trigger retry policy / alerting.

    elif event_type in (EventType.TRADE_EXECUTED.value, EventType.TRADE_FAILED.value):
        logger.info("Trade event received", event_type=event_type, payload=payload)
        # NOTE: trading_engine/ has no implementation yet (see README
        # "Known gaps" section) — this branch is a placeholder for when
        # that lands, not a working integration today.

    else:
        logger.warning("Unhandled event type", event_type=event_type)


async def main() -> None:
    consumer = EventConsumer(group_name="afm_worker")
    try:
        logger.info("AFM worker starting", stream="afm:events")
        await consumer.consume("afm:events", handle_event)
    finally:
        await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())
