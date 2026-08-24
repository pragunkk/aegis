"""Domain models representing database entities."""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    mrp: float
    price_floor: float
    stock: int = 0
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    razorpay_order_id: str
    agent_id: str
    product_id: Optional[str] = None
    negotiated_price: float
    currency: str = "INR"
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: Optional[str] = None
    agent_id: Optional[str] = None
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
