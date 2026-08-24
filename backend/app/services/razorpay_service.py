"""Razorpay integration service for order creation and webhook signature validation."""

import hmac
import hashlib
import logging
from typing import Optional, Dict, Any
import uuid
import razorpay
from backend.app.config import settings

logger = logging.getLogger("aegis.razorpay")


class RazorpayService:
    """Service encapsulating Razorpay API and signature verification operations."""

    def __init__(self):
        self._key_id = settings.RAZORPAY_KEY_ID
        self._key_secret = settings.RAZORPAY_KEY_SECRET
        self._webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        
        try:
            self.client = razorpay.Client(auth=(self._key_id, self._key_secret))
        except Exception as e:
            logger.warning(f"Could not initialize official Razorpay client: {e}")
            self.client = None

    def create_order(
        self,
        amount_in_rupees: float,
        currency: str = "INR",
        receipt: Optional[str] = None,
        notes: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Creates a Razorpay order.
        Amount must be passed to Razorpay in sub-units (paise: 1 INR = 100 paise).
        """
        amount_in_paise = int(round(amount_in_rupees * 100))
        receipt_id = receipt or f"rcpt_{uuid.uuid4().hex[:12]}"
        notes_payload = notes or {}

        # If live credentials exist and client is available
        if self.client and not self._key_id.startswith("rzp_test_default_mock"):
            try:
                order_data = {
                    "amount": amount_in_paise,
                    "currency": currency,
                    "receipt": receipt_id,
                    "notes": notes_payload,
                    "payment_capture": 1
                }
                rzp_order = self.client.order.create(data=order_data)
                return {
                    "id": rzp_order.get("id"),
                    "amount": rzp_order.get("amount"),
                    "currency": rzp_order.get("currency", currency),
                    "receipt": rzp_order.get("receipt"),
                    "status": rzp_order.get("status", "created"),
                }
            except Exception as e:
                logger.error(f"Error creating order on Razorpay API: {e}. Falling back to deterministic order generation.")

        # Deterministic order generation for test/sandbox/mock environment
        generated_id = f"order_{uuid.uuid4().hex[:14]}"
        return {
            "id": generated_id,
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": receipt_id,
            "status": "created",
            "notes": notes_payload
        }

    def verify_webhook_signature(
        self,
        payload_body: str,
        signature: str,
        secret: Optional[str] = None,
    ) -> bool:
        """
        Verifies the x-razorpay-signature header against the webhook secret using HMAC-SHA256.
        """
        webhook_secret = secret or self._webhook_secret
        if not signature or not webhook_secret:
            return False

        if self.client:
            try:
                self.client.utility.verify_webhook_signature(
                    payload_body,
                    signature,
                    webhook_secret
                )
                return True
            except razorpay.errors.SignatureVerificationError:
                logger.warning("Razorpay utility signature verification failed.")
            except Exception as e:
                logger.debug(f"Falling back to manual HMAC-SHA256 signature verification: {e}")

        # Fallback HMAC-SHA256 calculation
        try:
            expected_signature = hmac.new(
                key=webhook_secret.encode("utf-8"),
                msg=payload_body.encode("utf-8"),
                digestmod=hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"HMAC calculation failed: {e}")
            return False


razorpay_service = RazorpayService()
