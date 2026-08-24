"""Pydantic API request and response schemas for AegisPay Gateway."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class AP2MandatePayload(BaseModel):
    """Payload format for cryptographic AP2 Delegated Intent Tokens (DIT)."""
    sub: str = Field(..., description="Agent ID or Subject Identifier")
    max_budget: float = Field(..., description="Maximum budget authorized for this mandate")
    currency: str = Field(default="INR", description="Authorized currency")
    exp: Optional[int] = Field(None, description="Expiration UNIX timestamp")
    iat: Optional[int] = Field(None, description="Issued at UNIX timestamp")
    merchant_id: Optional[str] = Field(None, description="Optional restriction on target merchant")
    scope: Optional[List[str]] = Field(default_factory=lambda: ["commerce:negotiate", "commerce:transact"])

    @field_validator("max_budget")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("max_budget must be strictly positive")
        return v


class ProductPublicResponse(BaseModel):
    """Publicly visible product information (price_floor is confidential and excluded)."""
    id: str
    name: str
    description: Optional[str] = None
    mrp: float
    stock: int
    similarity_score: Optional[float] = None


class DiscoveryQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    limit: int = Field(default=5, ge=1, le=50)


class NegotiateRequest(BaseModel):
    product_id: str = Field(..., description="UUID of target product")
    proposed_price: float = Field(..., description="Price proposed by AI agent")
    reasoning: Optional[str] = Field(None, description="Agent reasoning or negotiation prompt context")

    @field_validator("proposed_price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("proposed_price must be greater than 0")
        return v


class NegotiationDecision(BaseModel):
    status: str  # "ACCEPTED", "REJECTED", "COUNTER_OFFER"
    message: str
    product_id: str
    negotiated_price: Optional[float] = None
    counter_offer: Optional[float] = None
    razorpay_order_id: Optional[str] = None
    amount_in_subunits: Optional[int] = None # e.g. paise
    currency: str = "INR"
    checkout_url: Optional[str] = None


class NegotiateResponse(BaseModel):
    success: bool
    decision: NegotiationDecision
    audit_event_id: Optional[str] = None


class RazorpayWebhookPayload(BaseModel):
    event: str
    payload: Dict[str, Any]
    created_at: Optional[int] = None


class AuditLogResponse(BaseModel):
    id: str
    order_id: Optional[str] = None
    agent_id: Optional[str] = None
    event_type: str
    payload: Dict[str, Any]
    created_at: Optional[datetime] = None
