from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.task import (
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from langflow.services.database.models.workspace import Workspace, WorkspaceMember

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead, status_code=201)
async def create_task(
    *,
    session: DbSession,
    task: TaskCreate,
    current_user: CurrentActiveUser,
):
    """Create a new task."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == task.workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role.in_(["owner", "editor"])
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you don't have permission to create tasks in it",
            )
        
        # Create the task
        db_task = Task(
            **task.model_dump(),
            created_by=current_user.id,
        )
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)
        return db_task
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create task: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/", response_model=list[TaskRead], status_code=200)
async def read_tasks(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    client_id: UUID | None = None,
    invoice_id: UUID | None = None,
    opportunity_id: UUID | None = None,
    assigned_to: UUID | None = None,
    status: str | None = None,
    priority: str | None = None,
):
    """Get all tasks the user has access to."""
    try:
        # Base query to get tasks from workspaces the user has access to
        query = (
            select(Task)
            .where(
                or_(
                    Task.workspace_id.in_(
                        select(Workspace.id)
                        .where(Workspace.owner_id == current_user.id)
                    ),
                    Task.workspace_id.in_(
                        select(WorkspaceMember.workspace_id)
                        .where(WorkspaceMember.user_id == current_user.id)
                    )
                )
            )
        )
        
        # Add filters if provided
        if workspace_id:
            query = query.where(Task.workspace_id == workspace_id)
        
        if client_id:
            query = query.where(Task.client_id == client_id)
        
        if invoice_id:
            query = query.where(Task.invoice_id == invoice_id)
        
        if opportunity_id:
            query = query.where(Task.opportunity_id == opportunity_id)
        
        if assigned_to:
            query = query.where(Task.assigned_to == assigned_to)
        
        if status:
            query = query.where(Task.status == status)
        
        if priority:
            query = query.where(Task.priority == priority)
        
        # Execute query
        tasks = (await session.exec(query)).all()
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{task_id}", response_model=TaskRead, status_code=200)
async def read_task(
    *,
    session: DbSession,
    task_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific task."""
    try:
        # Check if user has access to the task's workspace
        task = (
            await session.exec(
                select(Task)
                .where(
                    Task.id == task_id,
                    or_(
                        Task.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Task.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or access denied",
            )
        
        return task
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{task_id}", response_model=TaskRead, status_code=200)
async def update_task(
    *,
    session: DbSession,
    task_id: UUID,
    task: TaskUpdate,
    current_user: CurrentActiveUser,
):
    """Update a task."""
    try:
        # Check if user has access to update the task
        db_task = (
            await session.exec(
                select(Task)
                .where(
                    Task.id == task_id,
                    or_(
                        Task.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Task.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role.in_(["owner", "editor"])
                            )
                        ),
                        # Allow users to update tasks assigned to them
                        Task.assigned_to == current_user.id
                    )
                )
            )
        ).first()
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or you don't have permission to update it",
            )
        
        # Update task fields
        task_data = task.model_dump(exclude_unset=True)
        for key, value in task_data.items():
            setattr(db_task, key, value)
        
        # Update the updated_at timestamp
        from datetime import datetime, timezone
        db_task.updated_at = datetime.now(timezone.utc)
        
        await session.commit()
        await session.refresh(db_task)
        return db_task
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    *,
    session: DbSession,
    task_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a task."""
    try:
        # Check if user has access to delete the task
        db_task = (
            await session.exec(
                select(Task)
                .where(
                    Task.id == task_id,
                    or_(
                        Task.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Task.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role == "owner"
                            )
                        ),
                        # Allow users to delete tasks they created
                        Task.created_by == current_user.id
                    )
                )
            )
        ).first()
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or you don't have permission to delete it",
            )
        
        await session.delete(db_task)
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
