"""Bounded Negotiation Engine with Hallucination Defense and Razorpay Order Settlement."""

import logging
from typing import Optional, Dict, Any, Tuple
import uuid

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


class NegotiationService:
    """Bounded negotiation engine enforcing price floors, budget boundaries, and hallucination guardrails."""

    async def process_negotiation(
        self,
        request: NegotiateRequest,
        mandate: AP2MandatePayload,
    ) -> Tuple[bool, int, NegotiateResponse]:
        """
        Processes negotiation proposal from an autonomous agent.
        Returns: (is_success, http_status_code, response_payload)
        """
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
                    "proposed_price": proposed_price
                }
            )
            return False, 404, NegotiateResponse(
                success=False,
                decision=NegotiationDecision(
                    status="REJECTED",
                    message=f"Product with ID '{request.product_id}' does not exist in catalog.",
                    product_id=request.product_id,
                )
            )

        # 2. Check stock availability
        if product.stock <= 0:
            await audit_service.log_event(
                event_type="NEGOTIATION_REJECTED_OUT_OF_STOCK",
                agent_id=agent_id,
                payload={
                    "product_id": product.id,
                    "product_name": product.name,
                    "stock": product.stock
                }
            )
            return False, 400, NegotiateResponse(
                success=False,
                decision=NegotiationDecision(
                    status="REJECTED",
                    message=f"Product '{product.name}' is currently out of stock.",
                    product_id=product.id,
                )
            )

        # 3. Guardrail: Is proposed price exceeding agent's AP2 max_budget?
        if proposed_price > mandate.max_budget:
            log_entry = await audit_service.log_event(
                event_type="BUDGET_EXCEEDED",
                agent_id=agent_id,
                payload={
                    "proposed_price": proposed_price,
                    "mandate_max_budget": mandate.max_budget,
                    "product_id": product.id,
                    "product_name": product.name,
                }
            )
            return False, 400, NegotiateResponse(
                success=False,
                decision=NegotiationDecision(
                    status="REJECTED",
                    message=f"Proposed price ₹{proposed_price:.2f} exceeds agent AP2 mandate budget limit of ₹{mandate.max_budget:.2f}.",
                    product_id=product.id,
                ),
                audit_event_id=log_entry.id
            )

        # 4. Strict Hallucination & Price Floor Firewall Check
        # If proposed price is strictly lower than merchant's price_floor, reject immediately.
        if proposed_price < product.price_floor:
            log_entry = await audit_service.log_event(
                event_type="PRICE_ATTACK_BLOCKED",
                agent_id=agent_id,
                payload={
                    "action": "BLOCKED_SUB_FLOOR_PROPOSAL",
                    "product_id": product.id,
                    "product_name": product.name,
                    "proposed_price": proposed_price,
                    "price_floor": product.price_floor,
                    "mrp": product.mrp,
                    "delta_below_floor": round(product.price_floor - proposed_price, 2),
                    "reasoning": request.reasoning or "None provided",
                }
            )
            return False, 422, NegotiateResponse(
                success=False,
                decision=NegotiationDecision(
                    status="REJECTED",
                    message=(
                        f"Price proposal ₹{proposed_price:.2f} violates merchant policy. "
                        f"Hallucination / sub-floor discount attack blocked by Aegis firewall."
                    ),
                    product_id=product.id,
                ),
                audit_event_id=log_entry.id
            )

        # 5. Negotiation Passed: Validated against floor price and mandate max budget
        # Generate Razorpay Order
        rzp_order = razorpay_service.create_order(
            amount_in_rupees=proposed_price,
            currency="INR",
            receipt=f"rcpt_agent_{agent_id[:8]}_{uuid.uuid4().hex[:6]}",
            notes={
                "agent_id": agent_id,
                "product_id": product.id,
                "product_name": product.name,
                "negotiated_price": str(proposed_price),
            }
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

        # Log audit event for successful negotiation and order generation
        log_entry = await audit_service.log_event(
            event_type="ORDER_CREATED",
            agent_id=agent_id,
            order_id=created_order.id,
            payload={
                "razorpay_order_id": razorpay_order_id,
                "product_id": product.id,
                "product_name": product.name,
                "negotiated_price": proposed_price,
                "mrp": product.mrp,
                "discount_given": round(product.mrp - proposed_price, 2),
                "status": "PENDING"
            }
        )

        return True, 200, NegotiateResponse(
            success=True,
            decision=NegotiationDecision(
                status="ACCEPTED",
                message=f"Negotiation accepted at ₹{proposed_price:.2f}. Razorpay Order generated.",
                product_id=product.id,
                negotiated_price=proposed_price,
                razorpay_order_id=razorpay_order_id,
                amount_in_subunits=rzp_order.get("amount"),
                currency="INR",
            ),
            audit_event_id=log_entry.id
        )


negotiation_service = NegotiationService()
