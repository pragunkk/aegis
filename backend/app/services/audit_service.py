"""Audit service for logging immutable security and transactional events."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

from backend.app.database import db
from backend.app.models.domain import AuditLog

logger = logging.getLogger("aegis.audit")


class AuditService:
    """Service to record immutable audit log entries."""

    async def log_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        order_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            id=str(uuid.uuid4()),
            order_id=order_id,
            agent_id=agent_id,
            event_type=event_type,
            payload=payload,
            created_at=datetime.now(timezone.utc),
        )
        logger.info(f"[AUDIT EVENT: {event_type}] Agent: {agent_id} Order: {order_id} Details: {payload}")
        return await db.insert_audit_log(log_entry)

    async def get_recent_logs(self, limit: int = 50) -> List[AuditLog]:
        return await db.get_audit_logs(limit=limit)


audit_service = AuditService()
