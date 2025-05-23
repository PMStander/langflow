"""Utility functions for CRM endpoints."""
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.workspace import Workspace, WorkspaceMember
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
            status_code=status.HTTP_404_NOT_FOUND,
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
