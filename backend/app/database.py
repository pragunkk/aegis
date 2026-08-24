"""Database connection and repository layer using Supabase Client."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from supabase import create_client, Client
from backend.app.config import get_settings
from backend.app.models.domain import Product, Order, AuditLog, OrderStatus

logger = logging.getLogger("aegis.database")
settings = get_settings()

# Initialize live Supabase Client
supabase: Optional[Client] = None

if (
    settings.SUPABASE_URL
    and settings.SUPABASE_KEY
    and "your-project" not in settings.SUPABASE_URL
    and "your-supabase" not in settings.SUPABASE_KEY
):
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info(f"Initialized live Supabase client for: {settings.SUPABASE_URL}")
    except Exception as e:
        logger.warning(f"Failed to connect to Supabase: {e}. Using fallback repository.")
else:
    logger.info("Supabase credentials not configured or placeholder detected. Operating with pre-seeded fallback store.")

# Default seed catalog
DEFAULT_PRODUCTS = [
    Product(
        id="a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        name="Neural Interface Cyber-Deck X9",
        description="High-bandwidth direct neural transceiver for autonomous agents and cyborg operators with encrypted sub-millisecond telemetry.",
        mrp=4500.00,
        price_floor=3800.00,
        stock=25,
    ),
    Product(
        id="b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        name="Quantum Stealth Recon Drone (V2)",
        description="Autonomous surveillance unit with low-observable metamaterial skin, LIDAR mesh routing, and edge AI compute.",
        mrp=12000.00,
        price_floor=9500.00,
        stock=10,
    ),
    Product(
        id="c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
        name="Aegis Obsidian Hardware Security Module",
        description="FIPS 140-3 Level 4 tamper-resistant cryptographic vault for autonomous payment key authorization and AP2 mandate validation.",
        mrp=7500.00,
        price_floor=6200.00,
        stock=15,
    ),
    Product(
        id="d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a",
        name="Hyper-Threaded Bio-Telemetry Sensor Suite",
        description="Non-invasive dermal sensor array with real-time biometric telemetry and secure Bluetooth Low Energy 5.4 uplink.",
        mrp=2800.00,
        price_floor=2200.00,
        stock=50,
    ),
]


class DatabaseRepository:
    """Unified repository layer executing live Supabase database operations."""

    def __init__(self):
        self._mock_products: Dict[str, Product] = {p.id: p for p in DEFAULT_PRODUCTS}
        self._mock_orders: Dict[str, Order] = {}
        self._mock_audit_logs: List[AuditLog] = []

    @property
    def client(self) -> Optional[Client]:
        global supabase
        if supabase is None and settings.SUPABASE_URL and settings.SUPABASE_KEY and "your-project" not in settings.SUPABASE_URL:
            try:
                supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            except Exception:
                pass
        return supabase

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Fetch single product by UUID from Supabase."""
        if self.client:
            try:
                res = self.client.table("products").select("*").eq("id", product_id).execute()
                if res.data and len(res.data) > 0:
                    return Product(**res.data[0])
            except Exception as e:
                logger.error(f"Supabase error fetching product {product_id}: {e}")
        return self._mock_products.get(product_id)

    async def list_products(self) -> List[Product]:
        """List all products in the catalog."""
        if self.client:
            try:
                res = self.client.table("products").select("*").execute()
                if res.data and len(res.data) > 0:
                    return [Product(**row) for row in res.data]
            except Exception as e:
                logger.error(f"Supabase error listing products: {e}")
        return list(self._mock_products.values())

    async def search_products(self, query: str, limit: int = 5) -> List[Product]:
        """
        Performs semantic matching on products catalog.
        Queries Supabase and performs tokenized score ranking.
        """
        products = await self.list_products()
        query_lower = query.lower()
        scored_products = []
        for p in products:
            score = 0.0
            if query_lower in p.name.lower():
                score += 0.8
            if p.description and query_lower in p.description.lower():
                score += 0.5
            # Token match scoring
            query_tokens = set(query_lower.split())
            name_tokens = set(p.name.lower().split())
            desc_tokens = set(p.description.lower().split()) if p.description else set()
            score += len(query_tokens.intersection(name_tokens)) * 0.3
            score += len(query_tokens.intersection(desc_tokens)) * 0.1
            scored_products.append((score, p))

        # Sort by score relevance
        scored_products.sort(key=lambda x: x[0], reverse=True)
        results = [p for score, p in scored_products if score > 0]
        if not results:
            results = [p for _, p in scored_products]
        return results[:limit]

    async def create_order(self, order: Order) -> Order:
        """Insert a newly negotiated order into Supabase."""
        if not order.created_at:
            order.created_at = datetime.now(timezone.utc)
        if not order.updated_at:
            order.updated_at = order.created_at

        if self.client:
            try:
                data = {
                    "id": str(order.id),
                    "razorpay_order_id": order.razorpay_order_id,
                    "agent_id": order.agent_id,
                    "product_id": str(order.product_id),
                    "negotiated_price": float(order.negotiated_price),
                    "currency": order.currency,
                    "status": order.status.value if hasattr(order.status, "value") else str(order.status),
                }
                self.client.table("orders").insert(data).execute()
            except Exception as e:
                logger.error(f"Supabase error creating order {order.id}: {e}")

        self._mock_orders[order.razorpay_order_id] = order
        return order

    async def get_order_by_razorpay_id(self, razorpay_order_id: str) -> Optional[Order]:
        """Fetch order by Razorpay Order ID from Supabase."""
        if self.client:
            try:
                res = self.client.table("orders").select("*").eq("razorpay_order_id", razorpay_order_id).execute()
                if res.data and len(res.data) > 0:
                    return Order(**res.data[0])
            except Exception as e:
                logger.error(f"Supabase error fetching order {razorpay_order_id}: {e}")
        return self._mock_orders.get(razorpay_order_id)

    async def update_order_status(self, razorpay_order_id: str, status: OrderStatus) -> Optional[Order]:
        """Update order status in Supabase."""
        order = await self.get_order_by_razorpay_id(razorpay_order_id)
        if not order:
            return None

        order.status = status
        order.updated_at = datetime.now(timezone.utc)

        if self.client:
            try:
                status_val = status.value if hasattr(status, "value") else str(status)
                self.client.table("orders").update({
                    "status": status_val,
                    "updated_at": order.updated_at.isoformat(),
                }).eq("razorpay_order_id", razorpay_order_id).execute()
            except Exception as e:
                logger.error(f"Supabase error updating order {razorpay_order_id}: {e}")

        self._mock_orders[razorpay_order_id] = order
        return order

    async def insert_audit_log(self, log: AuditLog) -> AuditLog:
        """Insert immutable audit log into Supabase."""
        if not log.created_at:
            log.created_at = datetime.now(timezone.utc)

        if self.client:
            try:
                data = {
                    "id": str(log.id),
                    "order_id": str(log.order_id) if log.order_id else None,
                    "agent_id": log.agent_id,
                    "event_type": log.event_type,
                    "payload": log.payload,
                }
                self.client.table("audit_logs").insert(data).execute()
            except Exception as e:
                logger.error(f"Supabase error logging audit event: {e}")

        self._mock_audit_logs.insert(0, log)
        return log

    async def get_audit_logs(self, limit: int = 50) -> List[AuditLog]:
        """Retrieve recent immutable audit logs from Supabase."""
        if self.client:
            try:
                res = self.client.table("audit_logs").select("*").order("created_at", desc=True).limit(limit).execute()
                if res.data:
                    return [AuditLog(**row) for row in res.data]
            except Exception as e:
                logger.error(f"Supabase error fetching audit logs: {e}")
        return self._mock_audit_logs[:limit]


# Global database repository singleton
db = DatabaseRepository()
