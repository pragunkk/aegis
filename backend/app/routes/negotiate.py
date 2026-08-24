"""Bounded negotiation route protected by AP2 Mandate firewall."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from backend.app.middleware.ap2_mandate import verify_agent_mandate
from backend.app.models.schemas import (
    AP2MandatePayload,
    NegotiateRequest,
    NegotiateResponse,
)
from backend.app.services.negotiation_service import negotiation_service

router = APIRouter(prefix="/api/v1/agent", tags=["Negotiation"])


@router.post(
    "/negotiate",
    response_model=NegotiateResponse,
    responses={
        200: {"description": "Negotiation accepted, Razorpay Order created"},
        400: {"description": "Budget exceeded or product out of stock"},
        403: {"description": "Invalid or expired AP2 mandate"},
        404: {"description": "Product not found"},
        422: {"description": "Sub-floor price attack / Hallucination blocked by firewall"},
    },
)
async def negotiate_price(
    req: NegotiateRequest,
    mandate: AP2MandatePayload = Depends(verify_agent_mandate),
):
    """
    Bounded negotiation endpoint for AI Buyer Agents.
    Enforces AP2 Mandate verification, hallucination firewall against price floor,
    and automatic Razorpay Order creation upon validation.
    """
    is_success, status_code, response_data = await negotiation_service.process_negotiation(
        request=req,
        mandate=mandate,
    )

    if status_code != status.HTTP_200_OK:
        return JSONResponse(
            status_code=status_code,
            content=response_data.model_dump(mode="json"),
        )

    return response_data
