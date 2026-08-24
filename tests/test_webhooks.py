"""Tests for Razorpay Webhook Signature Verification and Order Settlement."""

import hmac
import hashlib
import json
import pytest
from httpx import AsyncClient

from backend.app.config import settings
from backend.app.database import db
from backend.app.models.domain import Order, OrderStatus


def generate_razorpay_signature(payload_str: str, secret: str) -> str:
    """Generates valid HMAC-SHA256 signature for Razorpay webhook testing."""
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_str.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()


@pytest.mark.asyncio
async def test_webhook_order_paid_success(async_client: AsyncClient):
    """
    Test scenario: Razorpay sends a signed order.paid webhook.
    Expected: Signature is verified, order status updated to PAID, status: ok returned.
    """
    # Create test pending order in DB
    order_id = "order_test_settlement_001"
    await db.create_order(
        Order(
            razorpay_order_id=order_id,
            agent_id="agent_nexus_007",
            product_id="a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            negotiated_price=3800.0,
            status=OrderStatus.PENDING,
        )
    )

    payload = {
        "entity": "event",
        "event": "order.paid",
        "contains": ["payment", "order"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_001_xyz",
                    "order_id": order_id,
                    "amount": 380000,
                    "currency": "INR",
                    "status": "captured",
                }
            },
            "order": {
                "entity": {
                    "id": order_id,
                    "amount": 380000,
                    "status": "paid",
                }
            }
        },
        "created_at": 1724500000
    }

    body_str = json.dumps(payload)
    valid_sig = generate_razorpay_signature(body_str, settings.RAZORPAY_WEBHOOK_SECRET)

    response = await async_client.post(
        "/api/v1/webhooks/razorpay",
        content=body_str.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-razorpay-signature": valid_sig,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["order_updated"] is True

    # Verify database status is updated to PAID
    order = await db.get_order_by_razorpay_id(order_id)
    assert order is not None
    assert order.status == OrderStatus.PAID


@pytest.mark.asyncio
async def test_webhook_invalid_signature_rejected(async_client: AsyncClient):
    """
    Test scenario: Webhook payload sent with forged or mismatched signature.
    Expected: Rejected with HTTP 400 Bad Request.
    """
    payload = {"event": "order.paid", "payload": {}}
    body_str = json.dumps(payload)
    fake_sig = "a1b2c3d4e5f6g7h8i9j0invalid_signature"

    response = await async_client.post(
        "/api/v1/webhooks/razorpay",
        content=body_str.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-razorpay-signature": fake_sig,
        },
    )

    assert response.status_code == 400
    assert "Invalid Razorpay webhook signature" in response.json()["detail"]


@pytest.mark.asyncio
async def test_webhook_missing_signature_rejected(async_client: AsyncClient):
    """Test webhook without x-razorpay-signature header returns 400."""
    payload = {"event": "order.paid"}
    response = await async_client.post(
        "/api/v1/webhooks/razorpay",
        json=payload,
    )
    assert response.status_code == 400
    assert "Missing x-razorpay-signature" in response.json()["detail"]
