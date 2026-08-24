"""Razorpay webhook processing and deterministic order settlement."""

import json
import logging
from typing import Optional
from fastapi import APIRouter, Request, Header, HTTPException, status

from backend.app.database import db
from backend.app.models.domain import OrderStatus
from backend.app.services.audit_service import audit_service
from backend.app.services.razorpay_service import razorpay_service

logger = logging.getLogger("aegis.webhooks")

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(
    req: Request,
    x_razorpay_signature: Optional[str] = Header(None, alias="x-razorpay-signature"),
):
    """
    Deterministic settlement webhook handler.
    Verifies Razorpay HMAC signature and updates order status.
    """
    raw_body = await req.body()
    body_str = raw_body.decode("utf-8")

    if not x_razorpay_signature:
        await audit_service.log_event(
            event_type="WEBHOOK_REJECTED",
            payload={"reason": "Missing x-razorpay-signature header"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing x-razorpay-signature header",
        )

    # Cryptographic HMAC-SHA256 signature verification
    is_valid = razorpay_service.verify_webhook_signature(
        payload_body=body_str,
        signature=x_razorpay_signature,
    )

    if not is_valid:
        await audit_service.log_event(
            event_type="SIGNATURE_VERIFICATION_FAILED",
            payload={
                "received_signature": x_razorpay_signature,
                "reason": "Signature mismatch"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay webhook signature",
        )

    try:
        data = json.loads(body_str)
    except Exception as e:
        logger.error(f"Failed to parse webhook JSON body: {e}")
        raise HTTPException(status_code=400, detail="Malformed JSON in webhook body")

    event_type = data.get("event", "unknown")
    event_payload = data.get("payload", {})

    razorpay_order_id = None
    payment_id = None

    # Handle payment entity
    if "payment" in event_payload and "entity" in event_payload["payment"]:
        payment_entity = event_payload["payment"]["entity"]
        razorpay_order_id = payment_entity.get("order_id")
        payment_id = payment_entity.get("id")

    # Handle order entity fallback
    if not razorpay_order_id and "order" in event_payload and "entity" in event_payload["order"]:
        razorpay_order_id = event_payload["order"]["entity"].get("id")

    # Update database order status based on event
    updated_order = None
    if razorpay_order_id:
        if event_type in ["order.paid", "payment.captured"]:
            updated_order = await db.update_order_status(razorpay_order_id, OrderStatus.PAID)
            await audit_service.log_event(
                event_type="PAYMENT_CONFIRMED",
                order_id=updated_order.id if updated_order else None,
                payload={
                    "event": event_type,
                    "razorpay_order_id": razorpay_order_id,
                    "payment_id": payment_id,
                    "status": "PAID"
                }
            )
        elif event_type in ["payment.failed"]:
            updated_order = await db.update_order_status(razorpay_order_id, OrderStatus.FAILED)
            await audit_service.log_event(
                event_type="PAYMENT_FAILED",
                order_id=updated_order.id if updated_order else None,
                payload={
                    "event": event_type,
                    "razorpay_order_id": razorpay_order_id,
                    "payment_id": payment_id,
                    "status": "FAILED"
                }
            )

    return {
        "status": "ok",
        "event": event_type,
        "razorpay_order_id": razorpay_order_id,
        "order_updated": updated_order is not None,
    }
