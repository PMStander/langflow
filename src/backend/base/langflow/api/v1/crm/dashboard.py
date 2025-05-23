from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.workspace import Workspace, WorkspaceMember
from langflow.services.database.models.crm.client import Client
from langflow.services.database.models.crm.invoice import Invoice
from langflow.services.database.models.crm.opportunity import Opportunity
from langflow.services.database.models.crm.task import Task

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/workspace/{workspace_id}/stats", status_code=200)
async def get_workspace_stats(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get statistics for a specific workspace."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )
        
        # Get client count
        client_count = (
            await session.exec(
                select(func.count())
                .where(Client.workspace_id == workspace_id)
            )
        ).one()
        
        # Get active client count
        active_client_count = (
            await session.exec(
                select(func.count())
                .where(
                    Client.workspace_id == workspace_id,
                    Client.status == "active"
                )
            )
        ).one()
        
        # Get invoice count
        invoice_count = (
            await session.exec(
                select(func.count())
                .where(Invoice.workspace_id == workspace_id)
            )
        ).one()
        
        # Get total revenue (sum of paid invoices)
        total_revenue = (
            await session.exec(
                select(func.sum(Invoice.amount))
                .where(
                    Invoice.workspace_id == workspace_id,
                    Invoice.status == "paid"
                )
            )
        ).one() or 0
        
        # Get opportunity count
        opportunity_count = (
            await session.exec(
                select(func.count())
                .where(Opportunity.workspace_id == workspace_id)
            )
        ).one()
        
        # Get open opportunity value
        open_opportunity_value = (
            await session.exec(
                select(func.sum(Opportunity.value))
                .where(
                    Opportunity.workspace_id == workspace_id,
                    Opportunity.status.in_(["new", "qualified", "proposal", "negotiation"])
                )
            )
        ).one() or 0
        
        # Get task count by status
        open_tasks = (
            await session.exec(
                select(func.count())
                .where(
                    Task.workspace_id == workspace_id,
                    Task.status == "open"
                )
            )
        ).one()
        
        in_progress_tasks = (
            await session.exec(
                select(func.count())
                .where(
                    Task.workspace_id == workspace_id,
                    Task.status == "in_progress"
                )
            )
        ).one()
        
        completed_tasks = (
            await session.exec(
                select(func.count())
                .where(
                    Task.workspace_id == workspace_id,
                    Task.status == "completed"
                )
            )
        ).one()
        
        return {
            "clients": {
                "total": client_count,
                "active": active_client_count,
            },
            "invoices": {
                "total": invoice_count,
                "revenue": total_revenue,
            },
            "opportunities": {
                "total": opportunity_count,
                "open_value": open_opportunity_value,
            },
            "tasks": {
                "open": open_tasks,
                "in_progress": in_progress_tasks,
                "completed": completed_tasks,
            }
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/workspace/{workspace_id}/client-distribution", status_code=200)
async def get_client_distribution(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get client distribution by status for a specific workspace."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )
        
        # Get client count by status
        active_clients = (
            await session.exec(
                select(func.count())
                .where(
                    Client.workspace_id == workspace_id,
                    Client.status == "active"
                )
            )
        ).one()
        
        inactive_clients = (
            await session.exec(
                select(func.count())
                .where(
                    Client.workspace_id == workspace_id,
                    Client.status == "inactive"
                )
            )
        ).one()
        
        lead_clients = (
            await session.exec(
                select(func.count())
                .where(
                    Client.workspace_id == workspace_id,
                    Client.status == "lead"
                )
            )
        ).one()
        
        return {
            "active": active_clients,
            "inactive": inactive_clients,
            "lead": lead_clients,
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/workspace/{workspace_id}/recent-activity", status_code=200)
async def get_recent_activity(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
    limit: int = 10,
):
    """Get recent activity for a specific workspace."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )
        
        # Get recent clients
        recent_clients = (
            await session.exec(
                select(Client)
                .where(Client.workspace_id == workspace_id)
                .order_by(Client.created_at.desc())
                .limit(limit)
            )
        ).all()
        
        # Get recent invoices
        recent_invoices = (
            await session.exec(
                select(Invoice)
                .where(Invoice.workspace_id == workspace_id)
                .order_by(Invoice.created_at.desc())
                .limit(limit)
            )
        ).all()
        
        # Get recent opportunities
        recent_opportunities = (
            await session.exec(
                select(Opportunity)
                .where(Opportunity.workspace_id == workspace_id)
                .order_by(Opportunity.created_at.desc())
                .limit(limit)
            )
        ).all()
        
        # Get recent tasks
        recent_tasks = (
            await session.exec(
                select(Task)
                .where(Task.workspace_id == workspace_id)
                .order_by(Task.created_at.desc())
                .limit(limit)
            )
        ).all()
        
        # Combine and sort all recent activities
        activities = []
        
        for client in recent_clients:
            activities.append({
                "type": "client",
                "id": str(client.id),
                "name": client.name,
                "created_at": client.created_at,
                "created_by": str(client.created_by),
            })
        
        for invoice in recent_invoices:
            activities.append({
                "type": "invoice",
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "amount": invoice.amount,
                "status": invoice.status,
                "created_at": invoice.created_at,
                "created_by": str(invoice.created_by),
            })
        
        for opportunity in recent_opportunities:
            activities.append({
                "type": "opportunity",
                "id": str(opportunity.id),
                "name": opportunity.name,
                "value": opportunity.value,
                "status": opportunity.status,
                "created_at": opportunity.created_at,
                "created_by": str(opportunity.created_by),
            })
        
        for task in recent_tasks:
            activities.append({
                "type": "task",
                "id": str(task.id),
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "created_at": task.created_at,
                "created_by": str(task.created_by),
            })
        
        # Sort by created_at (newest first) and limit to requested number
        activities.sort(key=lambda x: x["created_at"], reverse=True)
        activities = activities[:limit]
        
        return activities
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
