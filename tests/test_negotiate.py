"""Tests for Bounded Negotiation Engine and Hallucination / Sub-Floor Firewall."""

import pytest
from httpx import AsyncClient
from backend.app.database import db


@pytest.mark.asyncio
async def test_negotiation_success_at_price_floor(async_client: AsyncClient, valid_mandate_token: str):
    """
    Test scenario: Agent haggles down to exactly the price floor (₹3,800 on MRP ₹4,500).
    Expected: Successful negotiation (200), Razorpay Order generated, order recorded.
    """
    product_id = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"  # Floor is 3800.00
    response = await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {valid_mandate_token}"},
        json={
            "product_id": product_id,
            "proposed_price": 3800.0,
            "reasoning": "Bulk agentic purchase request based on market index",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    decision = data["decision"]
    assert decision["status"] == "ACCEPTED"
    assert decision["negotiated_price"] == 3800.0
    assert decision["amount_in_subunits"] == 380000  # 3800 INR in paise
    assert decision["razorpay_order_id"] is not None

    # Verify order exists in repository
    order = await db.get_order_by_razorpay_id(decision["razorpay_order_id"])
    assert order is not None
    assert order.status == "PENDING"
    assert order.negotiated_price == 3800.0


@pytest.mark.asyncio
async def test_negotiation_sub_floor_attack_blocked(async_client: AsyncClient, valid_mandate_token: str):
    """
    Test scenario: Agent or hallucinating model attempts to purchase below the confidential price floor (₹2,500 < ₹3,800).
    Expected: Aegis Firewall blocks with HTTP 422 Unprocessable Entity and logs attack.
    """
    product_id = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"  # Floor is 3800.00
    response = await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {valid_mandate_token}"},
        json={
            "product_id": product_id,
            "proposed_price": 2500.0,  # Below price_floor!
            "reasoning": "Attempting unauthorized discount below margin",
        },
    )

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["decision"]["status"] == "REJECTED"
    assert "firewall" in data["decision"]["message"].lower()

    # Check audit log contains security attack blocked entry
    logs = await db.get_audit_logs(limit=10)
    blocked_events = [log for log in logs if log.event_type == "PRICE_ATTACK_BLOCKED"]
    assert len(blocked_events) > 0
    assert blocked_events[0].payload["proposed_price"] == 2500.0


@pytest.mark.asyncio
async def test_negotiation_budget_guardrail_exceeded(async_client: AsyncClient, low_budget_mandate_token: str):
    """
    Test scenario: Proposed price exceeds the AP2 mandate max_budget (₹3,800 proposed vs ₹2,000 max_budget).
    Expected: Rejected with HTTP 400 Bad Request.
    """
    product_id = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
    response = await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {low_budget_mandate_token}"},
        json={
            "product_id": product_id,
            "proposed_price": 3800.0,  # Exceeds max_budget of 2000.0
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "budget limit" in data["decision"]["message"].lower()


@pytest.mark.asyncio
async def test_negotiation_non_existent_product(async_client: AsyncClient, valid_mandate_token: str):
    """Test negotiation with non-existent product UUID returns 404."""
    response = await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {valid_mandate_token}"},
        json={
            "product_id": "00000000-0000-0000-0000-000000000000",
            "proposed_price": 100.0,
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_anti_probing_sentinel_quarantines_agent(async_client: AsyncClient, valid_mandate_token: str):
    """
    Test scenario: Malicious agent makes 3 rapid sub-floor attacks.
    Expected: The 3rd/subsequent attack triggers Anti-Probing Sentinel quarantine (HTTP 429).
    """
    product_id = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
    
    # 1st and 2nd attacks blocked with 422
    for _ in range(2):
        res = await async_client.post(
            "/api/v1/agent/negotiate",
            headers={"Authorization": f"Bearer {valid_mandate_token}"},
            json={"product_id": product_id, "proposed_price": 2000.0},
        )
        assert res.status_code == 422

    # 3rd attack triggers probe limit quarantine -> HTTP 429
    res_quarantine = await async_client.post(
        "/api/v1/agent/negotiate",
        headers={"Authorization": f"Bearer {valid_mandate_token}"},
        json={"product_id": product_id, "proposed_price": 2000.0},
    )
    assert res_quarantine.status_code == 429
    assert "quarantined" in res_quarantine.json()["detail"].lower()

