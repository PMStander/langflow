from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.task import (
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=201)
async def create_task(
    *,
    session: DbSession,
    task: TaskCreate,
    current_user: CurrentActiveUser,
):
    """Create a new task."""
    try:
        # Check if user has access to the workspace with edit permission
        await check_workspace_access(
            session,
            task.workspace_id,
            current_user,
            require_edit_permission=True
        )

        # Create the task
        db_task = Task(
            **task.model_dump(),
            created_by=current_user.id,
        )
        # Update timestamps
        update_entity_timestamps(db_task, is_new=True)
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


@router.get("", response_model=PaginatedResponse[TaskRead], status_code=200)
async def read_tasks(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    client_id: UUID | None = None,
    invoice_id: UUID | None = None,
    opportunity_id: UUID | None = None,
    assigned_to: UUID | None = None,
    task_status: str | None = None,
    priority: str | None = None,
    skip: int = 0,
    limit: int = 100,
    page: int | None = None,
):
    """
    Get all tasks the user has access to.

    Supports pagination with skip/limit or page/limit parameters.
    Returns a paginated response with items and metadata.
    """
    try:
        # Base query to get tasks from workspaces the user has access to
        query = (
            select(Task)
            .where(get_entity_access_filter(Task, current_user.id))
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

        if task_status:
            query = query.where(Task.status == task_status)

        if priority:
            query = query.where(Task.priority == priority)

        # Apply pagination and get items with metadata
        tasks, metadata = await paginate_query(
            session=session,
            query=query,
            skip=skip,
            limit=limit,
            page=page
        )

        # Return paginated response
        return PaginatedResponse(items=tasks, metadata=metadata)
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
        # Check if task exists and user has access to it
        task = (
            await session.exec(
                select(Task)
                .where(
                    Task.id == task_id,
                    get_entity_access_filter(Task, current_user.id)
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
        # First check if the task exists
        db_task = (
            await session.exec(
                select(Task)
                .where(Task.id == task_id)
            )
        ).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        # Check if user has edit permission for the task's workspace or is the assignee
        try:
            # Check workspace access
            await check_workspace_access(
                session,
                db_task.workspace_id,
                current_user,
                require_edit_permission=True
            )
        except HTTPException:
            # If not workspace access, check if user is the assignee
            if db_task.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to update this task",
                )

        # Update task fields and timestamps
        task_data = task.model_dump(exclude_unset=True)
        update_entity_timestamps(db_task, update_data=task_data)

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
        # First check if the task exists
        db_task = (
            await session.exec(
                select(Task)
                .where(Task.id == task_id)
            )
        ).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        # Check if user has owner permission for the task's workspace or created the task
        can_delete = False

        # Check if user created the task
        if db_task.created_by == current_user.id:
            can_delete = True

        # If not the creator, check workspace owner permission
        if not can_delete:
            try:
                await check_workspace_access(
                    session,
                    db_task.workspace_id,
                    current_user,
                    require_owner_permission=True
                )
                can_delete = True
            except HTTPException:
                pass

        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this task",
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
