"""Audit trail and monitoring endpoints."""

from typing import List
from fastapi import APIRouter, Query

from backend.app.models.schemas import AuditLogResponse
from backend.app.services.audit_service import audit_service

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(limit: int = Query(50, ge=1, le=200)):
    """Fetches the latest immutable audit logs recorded by AegisPay."""
    logs = await audit_service.get_recent_logs(limit=limit)
    return [
        AuditLogResponse(
            id=log.id,
            order_id=log.order_id,
            agent_id=log.agent_id,
            event_type=log.event_type,
            payload=log.payload,
            created_at=log.created_at,
        )
        for log in logs
    ]
