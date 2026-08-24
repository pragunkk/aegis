"""Tests for AP2 Mandate and DIT Security Middleware."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mandate_authorized_access(async_client: AsyncClient, valid_mandate_token: str):
    """Test valid AP2 mandate allows negotiation request to proceed to negotiation logic."""
    response = await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {valid_mandate_token}"},
        json={
            "product_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "proposed_price": 4000.0,
        },
    )
    # 4000 is >= price_floor (3800) and <= max_budget (10000), so should be accepted (200)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["decision"]["status"] == "ACCEPTED"
    assert data["decision"]["negotiated_price"] == 4000.0
    assert data["decision"]["razorpay_order_id"] is not None


@pytest.mark.asyncio
async def test_mandate_missing_token(async_client: AsyncClient):
    """Test missing token results in 401 Unauthorized."""
    response = await async_client.post(
        "/api/v1/agent/negotiate",
        json={
            "product_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "proposed_price": 4000.0,
        },
    )
    assert response.status_code == 401
    assert "Missing AP2 Mandate" in response.json()["detail"]


@pytest.mark.asyncio
async def test_mandate_invalid_signature(async_client: AsyncClient, invalid_signature_token: str):
    """Test token with forged signature is rejected with 403 Forbidden."""
    response = await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {invalid_signature_token}"},
        json={
            "product_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "proposed_price": 4000.0,
        },
    )
    assert response.status_code == 403
    assert "validation failed" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_mandate_expired_token(async_client: AsyncClient, expired_mandate_token: str):
    """Test expired token is rejected with 401 Unauthorized."""
    response = await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {expired_mandate_token}"},
        json={
            "product_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "proposed_price": 4000.0,
        },
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()
