"""Utility functions for CRM endpoints."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from .error_handling import get_http_status_code
from sqlmodel import select, or_, func

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.workspace import Workspace, WorkspaceMember
# These imports are used in other functions in this module
from langflow.services.database.models.crm.client import Client
from langflow.services.database.models.crm.invoice import Invoice
from langflow.services.database.models.crm.opportunity import Opportunity
from langflow.services.database.models.crm.task import Task


async def check_workspace_access(
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
    require_edit_permission: bool = False,
    require_owner_permission: bool = False,
):
    """
    Check if the user has access to the workspace and return the workspace if they do.

    Args:
        session: Database session
        workspace_id: ID of the workspace to check
        current_user: Current user
        require_edit_permission: Whether to require edit permission
        require_owner_permission: Whether to require owner permission

    Returns:
        The workspace if the user has access

    Raises:
        HTTPException: If the user doesn't have access to the workspace
    """
    # Base query to check if user has access to the workspace
    query = select(Workspace).where(
        Workspace.id == workspace_id,
        or_(
            # User is the owner of the workspace
            Workspace.owner_id == current_user.id,
            # User is a member of the workspace
            Workspace.id.in_(
                select(WorkspaceMember.workspace_id)
                .where(
                    WorkspaceMember.user_id == current_user.id,
                    # Add role filter if required
                    *(
                        [WorkspaceMember.role == "owner"]
                        if require_owner_permission
                        else [WorkspaceMember.role.in_(["owner", "editor"])]
                        if require_edit_permission
                        else []
                    )
                )
            )
        )
    )

    workspace = (await session.exec(query)).first()

    if not workspace:
        detail = "Workspace not found or access denied"
        if require_edit_permission:
            detail = "Workspace not found or you don't have edit permission"
        if require_owner_permission:
            detail = "Workspace not found or you don't have owner permission"

        raise HTTPException(
            status_code=get_http_status_code("HTTP_404_NOT_FOUND"),
            detail=detail,
        )

    return workspace


def get_workspace_access_filter(current_user_id: UUID):
    """
    Get a filter expression for queries that checks if the user has access to the workspace.

    Args:
        current_user_id: ID of the current user

    Returns:
        SQLAlchemy filter expression
    """
    return or_(
        # User is the owner of the workspace
        Workspace.owner_id == current_user_id,
        # User is a member of the workspace
        Workspace.id.in_(
            select(WorkspaceMember.workspace_id)
            .where(WorkspaceMember.user_id == current_user_id)
        )
    )


def get_entity_access_filter(entity_class, current_user_id: UUID):
    """
    Get a filter expression for queries that checks if the user has access to an entity.

    Args:
        entity_class: Entity class (Client, Invoice, etc.)
        current_user_id: ID of the current user

    Returns:
        SQLAlchemy filter expression
    """
    return or_(
        # User is the owner of the workspace that contains the entity
        entity_class.workspace_id.in_(
            select(Workspace.id)
            .where(Workspace.owner_id == current_user_id)
        ),
        # User is a member of the workspace that contains the entity
        entity_class.workspace_id.in_(
            select(WorkspaceMember.workspace_id)
            .where(WorkspaceMember.user_id == current_user_id)
        )
    )


def update_entity_timestamps(entity, update_data=None, is_new=False):
    """
    Update the timestamps of an entity.

    Args:
        entity: The entity to update
        update_data: Optional dictionary of update data
        is_new: Whether this is a new entity (to set created_at)

    Returns:
        The updated entity
    """
    current_time = datetime.now(timezone.utc)

    # Set created_at for new entities
    if is_new and hasattr(entity, 'created_at'):
        entity.created_at = current_time

    # Always update updated_at
    if hasattr(entity, 'updated_at'):
        entity.updated_at = current_time

    # Apply update data if provided
    if update_data:
        for key, value in update_data.items():
            setattr(entity, key, value)

    return entity


async def paginate_query(session, query, skip: int = 0, limit: int = 100, page: int = None):
    """
    Apply pagination to a SQLAlchemy query and return both the paginated items and metadata.

    Args:
        session: Database session
        query: The SQLAlchemy query to paginate
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        page: Page number (1-based, optional - if provided, skip will be calculated)

    Returns:
        Tuple of (items, metadata) where:
        - items: List of items from the paginated query
        - metadata: PaginationMetadata object with total count, page info, etc.
    """
    from langflow.api.v1.crm.models import PaginationMetadata

    # Ensure skip and limit are non-negative
    skip = max(0, skip)
    limit = max(0, limit)

    # If page is provided, calculate skip
    if page is not None and page > 0:
        skip = (page - 1) * limit
    else:
        # Calculate page from skip and limit
        page = (skip // limit) + 1 if limit > 0 else 1

    # Get total count using a separate query
    count_query = query.with_only_columns(func.count())
    total = (await session.exec(count_query)).one()

    # Apply pagination to the original query
    paginated_query = query.offset(skip).limit(limit)

    # Execute the paginated query
    items = (await session.exec(paginated_query)).all()

    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    next_page = page + 1 if has_next else None
    prev_page = page - 1 if has_prev else None

    # Create metadata object
    metadata = PaginationMetadata(
        total=total,
        page=page,
        size=limit,
        pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        next_page=next_page,
        prev_page=prev_page
    )

    return items, metadata
