"""Routes package for AegisPay Gateway."""
from .discovery import router as discovery_router
from .negotiate import router as negotiate_router
from .webhooks import router as webhooks_router
from .audit import router as audit_router
from .test_helpers import router as test_helpers_router

__all__ = [
    "discovery_router",
    "negotiate_router",
    "webhooks_router",
    "audit_router",
    "test_helpers_router",
]
