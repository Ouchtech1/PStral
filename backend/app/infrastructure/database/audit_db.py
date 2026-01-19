"""
Audit logging system for Pstral.
Logs all user actions for compliance and monitoring.
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "audit.db")


class AuditLog(BaseModel):
    id: int
    timestamp: str
    user_id: int
    username: str
    action: str
    resource: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = "success"


class AuditStats(BaseModel):
    total_requests: int
    requests_today: int
    unique_users: int
    top_actions: List[dict]


def init_audit_db():
    """Initialize the audit database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            resource TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            status TEXT DEFAULT 'success',
            response_time_ms INTEGER
        )
    """)
    
    # Create indexes for common queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)")
    
    conn.commit()
    conn.close()


def log_action(
    user_id: Optional[int],
    username: Optional[str],
    action: str,
    resource: str,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    response_time_ms: Optional[int] = None
):
    """Log a user action to the audit database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    details_json = json.dumps(details) if details else None
    
    cursor.execute("""
        INSERT INTO audit_logs 
        (user_id, username, action, resource, details, ip_address, user_agent, status, response_time_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        username or "anonymous",
        action,
        resource,
        details_json,
        ip_address,
        user_agent,
        status,
        response_time_ms
    ))
    
    conn.commit()
    conn.close()


def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[AuditLog]:
    """Retrieve audit logs with optional filters."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT id, timestamp, user_id, username, action, resource, details, ip_address, user_agent, status FROM audit_logs WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    
    if action:
        query += " AND action = ?"
        params.append(action)
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for row in rows:
        logs.append(AuditLog(
            id=row[0],
            timestamp=row[1],
            user_id=row[2],
            username=row[3],
            action=row[4],
            resource=row[5],
            details=row[6],
            ip_address=row[7],
            user_agent=row[8],
            status=row[9]
        ))
    
    return logs


def get_audit_stats() -> AuditStats:
    """Get audit statistics for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total requests
    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    total_requests = cursor.fetchone()[0]
    
    # Requests today
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE DATE(timestamp) = ?", (today,))
    requests_today = cursor.fetchone()[0]
    
    # Unique users
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM audit_logs WHERE user_id IS NOT NULL")
    unique_users = cursor.fetchone()[0]
    
    # Top actions
    cursor.execute("""
        SELECT action, COUNT(*) as count 
        FROM audit_logs 
        GROUP BY action 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_actions = [{"action": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return AuditStats(
        total_requests=total_requests,
        requests_today=requests_today,
        unique_users=unique_users,
        top_actions=top_actions
    )


def export_audit_logs(
    format: str = "json",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """Export audit logs to JSON or CSV format."""
    logs = get_audit_logs(limit=10000, start_date=start_date, end_date=end_date)
    
    if format == "json":
        return json.dumps([log.dict() for log in logs], indent=2, ensure_ascii=False)
    
    elif format == "csv":
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Timestamp", "User ID", "Username", "Action", "Resource", "Details", "IP Address", "Status"])
        
        for log in logs:
            writer.writerow([
                log.id, log.timestamp, log.user_id, log.username,
                log.action, log.resource, log.details, log.ip_address, log.status
            ])
        
        return output.getvalue()
    
    return ""

