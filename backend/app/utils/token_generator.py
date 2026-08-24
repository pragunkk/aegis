"""Utility to generate AP2 Delegated Intent Tokens (DIT)."""

from typing import Optional, List
from datetime import datetime, timezone, timedelta
from jose import jwt

from backend.app.config import settings


def create_agent_mandate_token(
    agent_id: str,
    max_budget: float,
    currency: str = "INR",
    expires_in_minutes: int = 60,
    merchant_id: Optional[str] = None,
    scope: Optional[List[str]] = None,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> str:
    """
    Creates a signed AP2 Delegated Intent Token (DIT) for an autonomous agent.
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_in_minutes)

    payload = {
        "sub": agent_id,
        "max_budget": float(max_budget),
        "currency": currency,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "scope": scope or ["commerce:negotiate", "commerce:transact"],
    }

    if merchant_id:
        payload["merchant_id"] = merchant_id

    key = secret_key or settings.AP2_SECRET_KEY
    alg = algorithm or settings.AP2_ALGORITHM

    token = jwt.encode(payload, key, algorithm=alg)
    return token
