"""AP2 Mandate and Delegated Intent Token (DIT) Security Verification Middleware."""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

from backend.app.config import settings
from backend.app.models.schemas import AP2MandatePayload
from backend.app.services.audit_service import audit_service

logger = logging.getLogger("aegis.security")
security = HTTPBearer(auto_error=False)


async def verify_agent_mandate(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> AP2MandatePayload:
    """
    FastAPI Security Dependency that validates the AP2 Mandate / Delegated Intent Token (DIT).
    Supports Asymmetric JWKS (ES256) dynamic issuer key retrieval and Symmetric (HS256) fallback.
    """
    if not credentials or not credentials.credentials:
        await audit_service.log_event(
            event_type="MANDATE_REJECTED",
            payload={"reason": "Missing Authorization Bearer token header"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing AP2 Mandate Bearer token in Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Check unverified claims to determine verification strategy (JWKS vs Symmetric)
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        issuer_url = unverified_payload.get("iss")

        # 1. Asymmetric JWKS Verification (AP2 Enterprise Protocol)
        if issuer_url and (issuer_url.startswith("http://") or issuer_url.startswith("https://")):
            try:
                jwks_client = PyJWKClient(f"{issuer_url.rstrip('/')}/.well-known/jwks.json")
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                raw_payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["ES256", "RS256"],
                    options={"require": ["exp", "sub", "max_budget"]},
                )
            except Exception as jwks_err:
                logger.warning(f"JWKS verification failed: {jwks_err}. Attempting local signing key fallback.")
                raw_payload = jwt.decode(
                    token,
                    settings.AP2_SECRET_KEY,
                    algorithms=[settings.AP2_ALGORITHM],
                )
        else:
            # 2. Symmetric Secret Key Verification (Local / Test Mode)
            raw_payload = jwt.decode(
                token,
                settings.AP2_SECRET_KEY,
                algorithms=[settings.AP2_ALGORITHM],
            )

        # Validate structure with Pydantic
        mandate = AP2MandatePayload(**raw_payload)

        # Check timestamp expiration
        if mandate.exp:
            current_ts = int(datetime.now(timezone.utc).timestamp())
            if current_ts > mandate.exp:
                await audit_service.log_event(
                    event_type="MANDATE_REJECTED",
                    agent_id=mandate.sub,
                    payload={"reason": "Token expired", "exp": mandate.exp, "now": current_ts},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="AP2 Mandate Expired. User must re-authorize.",
                )

        # Audit successful mandate verification
        await audit_service.log_event(
            event_type="MANDATE_VERIFIED",
            agent_id=mandate.sub,
            payload={
                "agent_id": mandate.sub,
                "max_budget": mandate.max_budget,
                "currency": mandate.currency,
                "scope": mandate.scope,
            },
        )

        return mandate

    except jwt.ExpiredSignatureError as e:
        logger.warning(f"AP2 Mandate token expired: {e}")
        await audit_service.log_event(
            event_type="MANDATE_REJECTED",
            payload={"reason": "AP2 Mandate Expired. User must re-authorize.", "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="AP2 Mandate Expired. User must re-authorize.",
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"AP2 Mandate cryptographic validation failed: {e}")
        await audit_service.log_event(
            event_type="MANDATE_REJECTED",
            payload={"reason": "Cryptographic signature verification failed", "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid AP2 mandate signature: AP2 Mandate Cryptographic Validation Failed ({str(e)})",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Mandate validation error: {e}")
        await audit_service.log_event(
            event_type="MANDATE_REJECTED",
            payload={"reason": "Invalid mandate parameters", "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid AP2 mandate: AP2 Mandate Cryptographic Validation Failed ({str(e)})",
        )


# Alias for backward compatibility
verify_ap2_mandate = verify_agent_mandate
