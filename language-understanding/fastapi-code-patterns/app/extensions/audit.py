"""Audit logging extension — demonstrates extending the codebase using the same patterns.

Extends the original codebase with:
  - AuditLog ORM model
  - AuditLogRepository (extends Repository[AuditLog])
  - AuditService (wraps repository with business semantics)
  - get_audit_service DI factory
"""

from datetime import datetime
from typing import Optional, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import Repository, get_db


class AuditLog:
    """Simplified ORM model — mirrors the User model pattern."""
    __tablename__ = "audit_logs"
    id: int
    username: str
    action: str
    resource: Optional[str] = None
    success: bool
    ip_address: Optional[str] = None
    timestamp: datetime


class AuditLogRepository(Repository[AuditLog]):
    """Concrete repository — only adds what Repository[T] doesn't provide."""

    async def find_by_user(
        self, db: AsyncSession, username: str, limit: int = 50
    ) -> list[AuditLog]:
        from sqlalchemy import select
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.username == username)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def find_by_action(
        self, db: AsyncSession, action: str, limit: int = 50
    ) -> list[AuditLog]:
        from sqlalchemy import select
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.action == action)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class AuditService:
    """Encapsulates audit logging business logic.

    Matches UserService's pattern: wraps a repository, adds meaning via method names.
    """

    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    async def log_action(
        self,
        db: AsyncSession,
        username: str,
        action: str,
        success: bool = True,
        resource: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            username=username,
            action=action,
            resource=resource,
            success=success,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
        )
        db.add(entry)
        await db.commit()
        return entry

    async def get_user_history(
        self, db: AsyncSession, username: str, limit: int = 50
    ) -> list[AuditLog]:
        return await self.repository.find_by_user(db, username, limit=limit)


async def get_audit_service() -> AuditService:
    """DI factory — same pattern as UserService instantiation in endpoints."""
    return AuditService(AuditLogRepository(AuditLog))


# ── Example: audit-wired endpoint ────────────────

# To wire audit into existing endpoints, add the `audit` dependency:
#
#   @app.post("/token")
#   async def login(
#       username: str,
#       password: str,
#       db: AsyncSession = Depends(get_db),
#       audit: AuditService = Depends(get_audit_service),
#   ):
#       ...
#       await audit.log_action(db, username, "LOGIN", success=bool(user))
#       ...
#
#   @app.get("/admin/users/")
#   @requires_role("admin")
#   async def list_users(
#       ...,
#       audit: AuditService = Depends(get_audit_service),
#   ):
#       ...
#       await audit.log_action(db, current_user.username, "LIST_USERS")
#       ...
