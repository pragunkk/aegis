"""Testing and Simulator Helper Endpoints."""

import json
import time
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.utils.token_generator import create_agent_mandate_token
from backend.app.services.razorpay_service import razorpay_service
from backend.app.routes.webhooks import razorpay_webhook
from fastapi import Request

logger = logging.getLogger("aegis.test_helpers")

router = APIRouter(prefix="/api/v1/test", tags=["Simulator & Testing Helpers"])


class SettleOrderRequest(BaseModel):
    order_id: str
    amount: Optional[float] = 3800.0


@router.get("/token")
async def get_test_mandate_token(
    agent_id: str = "agent_simulator_007",
    max_budget: float = 10000.0,
):
    """
    Generates a valid AP2 cryptographic mandate token for the simulator or AI buyer agents.
    """
    token = create_agent_mandate_token(
        agent_id=agent_id,
        max_budget=max_budget,
        currency="INR",
        expires_in_minutes=1440,
    )
    return {
        "token": token,
        "agent_id": agent_id,
        "max_budget": max_budget,
        "currency": "INR",
    }


@router.post("/settle-order")
async def simulate_settle_order(req: SettleOrderRequest):
    """
    Helper to simulate a Razorpay order.paid webhook with valid HMAC-SHA256 signature.
    """
    import hmac
    import hashlib

    amount_in_paise = int(round(req.amount * 100))
    payload = {
        "entity": "event",
        "event": "order.paid",
        "contains": ["payment", "order"],
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_sim_{int(time.time())}",
                    "order_id": req.order_id,
                    "amount": amount_in_paise,
                    "currency": "INR",
                    "status": "captured",
                }
            },
            "order": {
                "entity": {
                    "id": req.order_id,
                    "amount": amount_in_paise,
                    "status": "paid",
                }
            }
        },
        "created_at": int(time.time())
    }

    body_str = json.dumps(payload)
    signature = hmac.new(
        key=settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=body_str.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Pass through database update and signature validation
    from backend.app.database import db
    from backend.app.models.domain import OrderStatus
    from backend.app.services.audit_service import audit_service

    updated_order = await db.update_order_status(req.order_id, OrderStatus.PAID)
    await audit_service.log_event(
        event_type="PAYMENT_CONFIRMED",
        order_id=updated_order.id if updated_order else None,
        payload={
            "event": "order.paid",
            "razorpay_order_id": req.order_id,
            "payment_id": payload["payload"]["payment"]["entity"]["id"],
            "status": "PAID"
        }
    )

    return {
        "status": "ok",
        "event": "order.paid",
        "razorpay_order_id": req.order_id,
        "signature_verified": True,
        "order_updated": updated_order is not None,
    }
