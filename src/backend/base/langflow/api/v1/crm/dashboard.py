from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, case, cast, Float
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.workspace import Workspace, WorkspaceMember
from langflow.services.database.models.crm.client import Client
from langflow.services.database.models.crm.invoice import Invoice
from langflow.services.database.models.crm.opportunity import Opportunity
from langflow.services.database.models.crm.task import Task

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

async def check_workspace_access(session: DbSession, workspace_id: UUID, current_user: CurrentActiveUser):
    """Check if the user has access to the workspace and return the workspace if they do."""
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

    return workspace


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
        await check_workspace_access(session, workspace_id, current_user)

        # Get all stats in a single query using a dictionary of aggregations

        # Client stats
        client_stats = (
            await session.exec(
                select(
                    func.count().label("total_count"),
                    func.sum(case((Client.status == "active", 1), else_=0)).label("active_count")
                )
                .where(Client.workspace_id == workspace_id)
            )
        ).one()

        client_count = client_stats[0] if client_stats else 0
        active_client_count = client_stats[1] if client_stats and len(client_stats) > 1 else 0

        # Invoice stats
        invoice_stats = (
            await session.exec(
                select(
                    func.count().label("total_count"),
                    func.sum(case((Invoice.status == "paid", Invoice.amount), else_=0)).label("total_revenue")
                )
                .where(Invoice.workspace_id == workspace_id)
            )
        ).one()

        invoice_count = invoice_stats[0] if invoice_stats else 0
        total_revenue = invoice_stats[1] if invoice_stats and len(invoice_stats) > 1 and invoice_stats[1] is not None else 0

        # Opportunity stats
        opportunity_stats = (
            await session.exec(
                select(
                    func.count().label("total_count"),
                    func.sum(
                        case(
                            (Opportunity.status.in_(["new", "qualified", "proposal", "negotiation"]),
                             cast(Opportunity.value, Float)),
                            else_=0
                        )
                    ).label("open_value")
                )
                .where(Opportunity.workspace_id == workspace_id)
            )
        ).one()

        opportunity_count = opportunity_stats[0] if opportunity_stats else 0
        open_opportunity_value = opportunity_stats[1] if opportunity_stats and len(opportunity_stats) > 1 and opportunity_stats[1] is not None else 0

        # Task stats
        task_stats = (
            await session.exec(
                select(
                    func.sum(case((Task.status == "open", 1), else_=0)).label("open_count"),
                    func.sum(case((Task.status == "in_progress", 1), else_=0)).label("in_progress_count"),
                    func.sum(case((Task.status == "completed", 1), else_=0)).label("completed_count")
                )
                .where(Task.workspace_id == workspace_id)
            )
        ).one()

        open_tasks = task_stats[0] if task_stats and task_stats[0] is not None else 0
        in_progress_tasks = task_stats[1] if task_stats and len(task_stats) > 1 and task_stats[1] is not None else 0
        completed_tasks = task_stats[2] if task_stats and len(task_stats) > 2 and task_stats[2] is not None else 0

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
        await check_workspace_access(session, workspace_id, current_user)

        # Get client count by status in a single query using GROUP BY

        # Query to get counts by status
        client_distribution = {}

        # First, get all possible statuses to ensure we have entries for all
        possible_statuses = ["active", "inactive", "lead"]
        for status in possible_statuses:
            client_distribution[status] = 0

        # Then get the actual counts from the database
        status_counts = (
            await session.exec(
                select(
                    Client.status,
                    func.count().label("count")
                )
                .where(Client.workspace_id == workspace_id)
                .group_by(Client.status)
            )
        ).all()

        # Update the distribution dictionary with actual counts
        for status, count in status_counts:
            if status in client_distribution:
                client_distribution[status] = count

        return client_distribution
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
        await check_workspace_access(session, workspace_id, current_user)

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
