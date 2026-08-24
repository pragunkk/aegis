"""Tests for Audit Log Retrieval Endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_audit_logs(async_client: AsyncClient, valid_mandate_token: str):
    """Test retrieving immutable audit logs after operations."""
    # Perform a request that logs events
    await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {valid_mandate_token}"},
        json={
            "product_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "proposed_price": 3800.0,
        },
    )

    response = await async_client.get("/api/v1/audit/logs?limit=10")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
    assert len(logs) > 0

    event_types = [log["event_type"] for log in logs]
    assert "ORDER_CREATED" in event_types or "MANDATE_VERIFIED" in event_types
