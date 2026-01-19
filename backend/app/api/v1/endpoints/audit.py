"""
Audit endpoints for admin users.
Provides access to audit logs and statistics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from typing import Optional, List
from pydantic import BaseModel

from ....core.auth import User, get_admin_user
from ....infrastructure.database.audit_db import (
    AuditLog,
    AuditStats,
    get_audit_logs,
    get_audit_stats,
    export_audit_logs
)

router = APIRouter()


class AuditLogsResponse(BaseModel):
    logs: List[AuditLog]
    total: int
    page: int
    limit: int


@router.get("/logs", response_model=AuditLogsResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_admin_user)
):
    """
    Get paginated audit logs. Admin only.
    """
    offset = (page - 1) * limit
    logs = get_audit_logs(
        limit=limit,
        offset=offset,
        user_id=user_id,
        action=action,
        start_date=start_date,
        end_date=end_date
    )
    
    return AuditLogsResponse(
        logs=logs,
        total=len(logs),  # Simplified, in production would do a COUNT query
        page=page,
        limit=limit
    )


@router.get("/stats", response_model=AuditStats)
async def get_stats(current_user: User = Depends(get_admin_user)):
    """
    Get audit statistics. Admin only.
    """
    return get_audit_stats()


@router.get("/export")
async def export_logs(
    format: str = Query("json", regex="^(json|csv)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_admin_user)
):
    """
    Export audit logs in JSON or CSV format. Admin only.
    """
    content = export_audit_logs(format=format, start_date=start_date, end_date=end_date)
    
    if format == "json":
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=audit_logs.json"}
        )
    else:
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
        )

