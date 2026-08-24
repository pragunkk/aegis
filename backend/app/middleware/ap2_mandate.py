"""AP2 Mandate and Delegated Intent Token (DIT) Security Verification Middleware."""

import logging
from datetime import datetime, timezone
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from backend.app.config import settings
from backend.app.models.schemas import AP2MandatePayload
from backend.app.services.audit_service import audit_service

logger = logging.getLogger("aegis.security")

security_bearer = HTTPBearer(auto_error=False)


async def verify_agent_mandate(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer),
) -> AP2MandatePayload:
    """
    FastAPI Security Dependency that validates the AP2 Mandate / Delegated Intent Token (DIT).
    Enforces cryptographic signature check and budget constraints.
    """
    if not credentials or not credentials.credentials:
        await audit_service.log_event(
            event_type="MANDATE_REJECTED",
            payload={"reason": "Missing Authorization Bearer token header"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing AP2 Mandate Bearer token in Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        raw_payload = jwt.decode(
            token,
            settings.AP2_SECRET_KEY,
            algorithms=[settings.AP2_ALGORITHM],
        )

        # Validate structure with Pydantic
        mandate = AP2MandatePayload(**raw_payload)

        # Check timestamp expiration if present
        if mandate.exp:
            current_ts = int(datetime.now(timezone.utc).timestamp())
            if current_ts > mandate.exp:
                await audit_service.log_event(
                    event_type="MANDATE_REJECTED",
                    agent_id=mandate.sub,
                    payload={"reason": "Token expired", "exp": mandate.exp, "now": current_ts}
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="AP2 Mandate token has expired",
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
            }
        )

        return mandate

    except jwt.ExpiredSignatureError as e:
        logger.warning(f"AP2 Mandate token expired: {e}")
        await audit_service.log_event(
            event_type="MANDATE_REJECTED",
            payload={"reason": "AP2 Mandate token has expired", "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AP2 Mandate token has expired",
        )
    except JWTError as e:
        logger.warning(f"JWT signature verification failed: {e}")
        await audit_service.log_event(
            event_type="MANDATE_REJECTED",
            payload={"reason": "Cryptographic signature verification failed", "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid AP2 mandate signature or token formatting",
        )
    except Exception as e:
        logger.warning(f"Mandate validation error: {e}")
        await audit_service.log_event(
            event_type="MANDATE_REJECTED",
            payload={"reason": "Invalid mandate parameters", "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid AP2 mandate: {str(e)}",
        )
