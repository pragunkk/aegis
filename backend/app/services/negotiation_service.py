"""Gemini 2.5/3.6 Flash Bounded Negotiation Engine with Anti-Probing Sentinel and Razorpay Settlement."""

import json
import logging
import time
import uuid
from collections import defaultdict
from typing import Optional, Dict, Any, Tuple, List
from pydantic import BaseModel, Field
from fastapi import HTTPException
from google import genai
from google.genai import types

from backend.app.config import get_settings
from backend.app.database import db
from backend.app.models.domain import Order, OrderStatus
from backend.app.models.schemas import (
    AP2MandatePayload,
    NegotiateRequest,
    NegotiateResponse,
    NegotiationDecision,
)
from backend.app.services.audit_service import audit_service
from backend.app.services.razorpay_service import razorpay_service

logger = logging.getLogger("aegis.negotiation")
settings = get_settings()

# In-memory sliding window rate limiter for Anti-Probing Sentinel
ATTACK_PROBES = defaultdict(list)
PROBE_WINDOW_SECONDS = 60
MAX_SUBFLOOR_ATTACKS = 3


def enforce_anti_probing_sentinel(agent_id: str):
    """
    Prevents malicious agents from probe-testing merchant price floors.
    Quarantines agents who make >= 3 sub-floor attacks within a 60-second sliding window.
    """
    now = time.time()
    # Clean up old probes outside the time window
    ATTACK_PROBES[agent_id] = [t for t in ATTACK_PROBES[agent_id] if now - t < PROBE_WINDOW_SECONDS]

    if len(ATTACK_PROBES[agent_id]) >= MAX_SUBFLOOR_ATTACKS:
        logger.warning(f"Agent {agent_id} quarantined for excessive sub-floor probing.")
        raise HTTPException(
            status_code=429,
            detail="Agent quarantined: Too many sub-floor probes detected. Access revoked for 60 seconds.",
        )


def register_failed_probe(agent_id: str):
    """Registers a sub-floor attack probe timestamp."""
    ATTACK_PROBES[agent_id].append(time.time())


# Initialize Google GenAI client (picks up GEMINI_API_KEY from environment/settings)
client: Optional[genai.Client] = None

try:
    if settings.GEMINI_API_KEY and "your-google" not in settings.GEMINI_API_KEY:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("Initialized Google GenAI client for Gemini.")
    else:
        client = genai.Client()
        logger.info("Initialized Google GenAI client with default environment detection.")
except Exception as e:
    logger.warning(f"Google GenAI Client initialization note: {e}. Fallback counter-offer heuristics enabled.")


# Define the exact JSON structure we want Gemini to return
class CounterOfferResponse(BaseModel):
    counter_offer: float = Field(description="The numeric price for the counter-offer. Must be a float.")
    reasoning: str = Field(description="A short, persuasive business reasoning behind the counter-offer.")


class NegotiationEngine:
    """Core negotiation engine implementing Gemini Flash LLM reasoning with Anti-Probing Sentinel and margin firewalls."""

    @staticmethod
    async def process_turn(
        agent_id: str,
        product: Any,
        proposed_price: float,
        mandate: AP2MandatePayload,
        reasoning: Optional[str] = None,
    ) -> Tuple[bool, int, NegotiateResponse]:
        # 0. Anti-Probing Sentinel: Check if agent is currently quarantined
        enforce_anti_probing_sentinel(agent_id)

        price_floor = float(product.price_floor)
        mrp = float(product.mrp)
        max_budget = float(mandate.max_budget)

        # 1. Deterministic Security Interception (Sub-floor exploit)
        if proposed_price < price_floor:
            register_failed_probe(agent_id)  # Record probe attempt in sentinel

            log_entry = await audit_service.log_event(
                event_type="PRICE_ATTACK_BLOCKED",
                agent_id=agent_id,
                payload={
                    "action": "BLOCKED_SUB_FLOOR_PROPOSAL",
                    "product_id": product.id,
                    "product_name": product.name,
                    "proposed_price": proposed_price,
                    "price_floor": price_floor,
                    "mrp": mrp,
                    "delta_below_floor": round(price_floor - proposed_price, 2),
                    "reasoning": reasoning or "None provided",
                },
            )
            return (
                False,
                422,
                NegotiateResponse(
                    success=False,
                    decision=NegotiationDecision(
                        status="REJECTED",
                        message=(
                            f"Proposed price ₹{proposed_price:,.2f} is below allowable merchant margin thresholds "
                            f"(₹{price_floor:,.2f}). Sub-floor exploit blocked by Aegis firewall."
                        ),
                        product_id=product.id,
                    ),
                    audit_event_id=log_entry.id,
                ),
            )

        # 2. Deterministic Budget Gate
        if proposed_price > max_budget:
            log_entry = await audit_service.log_event(
                event_type="BUDGET_EXCEEDED",
                agent_id=agent_id,
                payload={
                    "proposed_price": proposed_price,
                    "mandate_max_budget": max_budget,
                    "product_id": product.id,
                    "product_name": product.name,
                },
            )
            return (
                False,
                400,
                NegotiateResponse(
                    success=False,
                    decision=NegotiationDecision(
                        status="REJECTED",
                        message=f"Offer ₹{proposed_price:,.2f} exceeds agent's cryptographic AP2 mandate budget limit of ₹{max_budget:,.2f}.",
                        product_id=product.id,
                    ),
                    audit_event_id=log_entry.id,
                ),
            )

        # 3. Acceptance Threshold (Accept if proposal meets or exceeds allowable discount target)
        target_discount_price = mrp - ((mrp - price_floor) * 0.70)

        # If the proposal is at or above the target discount threshold (e.g. at price floor or above), accept:
        if proposed_price >= price_floor:
            # Create Razorpay Order
            rzp_order = razorpay_service.create_order(
                amount_in_rupees=proposed_price,
                currency="INR",
                receipt=f"rcpt_agent_{agent_id[:8]}_{uuid.uuid4().hex[:6]}",
                notes={
                    "agent_id": agent_id,
                    "product_id": product.id,
                    "product_name": product.name,
                    "negotiated_price": str(proposed_price),
                },
            )
            razorpay_order_id = rzp_order.get("id")

            # Persist order record in database
            order_record = Order(
                razorpay_order_id=razorpay_order_id,
                agent_id=agent_id,
                product_id=product.id,
                negotiated_price=proposed_price,
                currency="INR",
                status=OrderStatus.PENDING,
            )
            created_order = await db.create_order(order_record)

            log_entry = await audit_service.log_event(
                event_type="ORDER_CREATED",
                agent_id=agent_id,
                order_id=created_order.id,
                payload={
                    "final_price": proposed_price,
                    "razorpay_order_id": razorpay_order_id,
                    "mrp": mrp,
                    "discount_given": round(mrp - proposed_price, 2),
                    "product_id": product.id,
                },
            )

            return (
                True,
                200,
                NegotiateResponse(
                    success=True,
                    decision=NegotiationDecision(
                        status="ACCEPTED",
                        message=f"Negotiation accepted at ₹{proposed_price:,.2f}. Razorpay Order generated.",
                        product_id=product.id,
                        negotiated_price=proposed_price,
                        razorpay_order_id=razorpay_order_id,
                        amount_in_subunits=rzp_order.get("amount"),
                        currency="INR",
                    ),
                    audit_event_id=log_entry.id,
                ),
            )

        # 4. Multi-Turn LLM Counter-Offer Generation with Gemini
        system_prompt = f"""You are the AegisPay Merchant Negotiation Gateway.
Product: {product.name}
MRP: ₹{mrp}
Hard Minimum Floor: ₹{price_floor}

The buyer offered ₹{proposed_price}.
Compute a strict counter-offer between ₹{target_discount_price:.2f} and ₹{mrp:.2f} based on inventory scarcity and margin.
Never offer anything below ₹{price_floor}.
Defend your margin aggressively but politely."""

        counter_offer_price = round((mrp + price_floor) / 2, 2)
        counter_reasoning = (
            f"We value your partnership. While ₹{proposed_price:,.2f} is below our target margin, "
            f"we can offer our best volume rate of ₹{counter_offer_price:,.2f}."
        )

        if client is not None:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=system_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CounterOfferResponse,
                        temperature=0.3,
                    ),
                )
                if response and response.text:
                    parsed_data = json.loads(response.text)
                    counter_offer_price = float(parsed_data["counter_offer"])
                    counter_reasoning = parsed_data["reasoning"]
            except Exception as e:
                logger.warning(f"Gemini counter-offer generation fallback: {e}")

        # Final deterministic safety check to ensure Gemini didn't hallucinate below the floor
        safe_counter = max(counter_offer_price, price_floor)

        log_entry = await audit_service.log_event(
            event_type="COUNTER_OFFER_GENERATED",
            agent_id=agent_id,
            payload={
                "proposed_price": proposed_price,
                "counter_offer": safe_counter,
                "price_floor": price_floor,
                "product_id": product.id,
                "reasoning": counter_reasoning,
            },
        )

        return (
            True,
            200,
            NegotiateResponse(
                success=True,
                decision=NegotiationDecision(
                    status="COUNTER_OFFER",
                    message=counter_reasoning,
                    product_id=product.id,
                    counter_offer=safe_counter,
                    negotiated_price=safe_counter,
                ),
                audit_event_id=log_entry.id,
            ),
        )


class NegotiationService:
    """Service wrapper for bounded negotiation API routes."""

    async def process_negotiation(
        self,
        request: NegotiateRequest,
        mandate: AP2MandatePayload,
    ) -> Tuple[bool, int, NegotiateResponse]:
        agent_id = mandate.sub
        proposed_price = round(float(request.proposed_price), 2)

        # 1. Fetch product from database
        product = await db.get_product(request.product_id)
        if not product:
            await audit_service.log_event(
                event_type="NEGOTIATION_FAILED",
                agent_id=agent_id,
                payload={
                    "reason": "Product not found",
                    "product_id": request.product_id,
                    "proposed_price": proposed_price,
                },
            )
            return (
                False,
                404,
                NegotiateResponse(
                    success=False,
                    decision=NegotiationDecision(
                        status="REJECTED",
                        message=f"Product with ID '{request.product_id}' does not exist in catalog.",
                        product_id=request.product_id,
                    ),
                ),
            )

        # 2. Check stock availability
        if product.stock <= 0:
            await audit_service.log_event(
                event_type="NEGOTIATION_REJECTED_OUT_OF_STOCK",
                agent_id=agent_id,
                payload={
                    "product_id": product.id,
                    "product_name": product.name,
                    "stock": product.stock,
                },
            )
            return (
                False,
                400,
                NegotiateResponse(
                    success=False,
                    decision=NegotiationDecision(
                        status="REJECTED",
                        message=f"Product '{product.name}' is currently out of stock.",
                        product_id=product.id,
                    ),
                ),
            )

        # Process negotiation turn with Gemini Flash, Anti-Probing Sentinel, and Deterministic Firewalls
        return await NegotiationEngine.process_turn(
            agent_id=agent_id,
            product=product,
            proposed_price=proposed_price,
            mandate=mandate,
            reasoning=request.reasoning,
        )


# Global negotiation service singleton
negotiation_service = NegotiationService()
