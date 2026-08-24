"""Middleware package for AegisPay Gateway."""
from .ap2_mandate import verify_agent_mandate

__all__ = ["verify_agent_mandate"]
