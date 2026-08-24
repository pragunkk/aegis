"""Pytest fixtures and configuration."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.utils.token_generator import create_agent_mandate_token


@pytest.fixture
def valid_mandate_token():
    """Generates a valid AP2 mandate token with ₹10,000 budget."""
    return create_agent_mandate_token(
        agent_id="agent_nexus_007",
        max_budget=10000.0,
        currency="INR",
        expires_in_minutes=60,
    )


@pytest.fixture
def low_budget_mandate_token():
    """Generates an AP2 mandate token with a low budget of ₹2,000."""
    return create_agent_mandate_token(
        agent_id="agent_budget_restricted",
        max_budget=2000.0,
        currency="INR",
        expires_in_minutes=60,
    )


@pytest.fixture
def expired_mandate_token():
    """Generates an expired AP2 mandate token."""
    return create_agent_mandate_token(
        agent_id="agent_expired",
        max_budget=10000.0,
        currency="INR",
        expires_in_minutes=-10,  # Expired in past
    )


@pytest.fixture
def invalid_signature_token():
    """Generates a token signed with an unauthorized secret key."""
    return create_agent_mandate_token(
        agent_id="agent_malicious",
        max_budget=10000.0,
        currency="INR",
        secret_key="malicious_unauthorized_key",
    )


@pytest.fixture
async def async_client():
    """Asynchronous test client for FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
