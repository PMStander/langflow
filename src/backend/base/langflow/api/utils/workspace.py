from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select, or_

from langflow.services.database.models.folder.model import Folder
from langflow.services.database.models.workspace.model import Workspace, WorkspaceMember


async def verify_workspace_access(
    session,
    workspace_id: UUID,
    user_id: UUID,
    required_role: Optional[str] = None,
):
    """
    Verify if a user has access to a workspace.

    Args:
        session: Database session
        workspace_id: Workspace ID
        user_id: User ID
        required_role: Required role (owner, editor, viewer). If None, any role is allowed.

    Returns:
        True if user has access, False otherwise

    Raises:
        HTTPException: If user doesn't have access to the workspace
    """
    # Check if user is the owner of the workspace
    workspace = (
        await session.exec(
            select(Workspace)
            .where(
                Workspace.id == workspace_id,
                Workspace.owner_id == user_id
            )
        )
    ).first()

    if workspace:
        # User is the owner, they have all permissions
        return True

    # Check if user is a member of the workspace
    workspace_member = (
        await session.exec(
            select(WorkspaceMember)
            .where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id
            )
        )
    ).first()

    if not workspace_member:
        # User is not a member of the workspace
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    # If a specific role is required, check if user has that role
    if required_role and workspace_member.role != required_role:
        # Check if user has a higher role
        if required_role == "viewer":
            # Any role can view
            return True
        elif required_role == "editor" and workspace_member.role == "owner":
            # Owner can edit
            return True
        else:
            # User doesn't have the required role
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You need {required_role} permissions for this action",
            )

    return True


async def get_folder_workspace_id(session, folder_id: UUID):
    """
    Get the workspace ID for a folder.

    Args:
        session: Database session
        folder_id: Folder ID

    Returns:
        Workspace ID or None if folder doesn't have a workspace
    """
    folder = (
        await session.exec(
            select(Folder)
            .where(Folder.id == folder_id)
        )
    ).first()

    if not folder:
        return None

    return folder.workspace_id


async def verify_folder_access(
    session,
    folder_id: UUID,
    user_id: UUID,
    required_role: Optional[str] = None,
):
    """
    Verify if a user has access to a folder through workspace permissions.

    Args:
        session: Database session
        folder_id: Folder ID
        user_id: User ID
        required_role: Required role (owner, editor, viewer). If None, any role is allowed.

    Returns:
        True if user has access, False otherwise

    Raises:
        HTTPException: If user doesn't have access to the folder
    """
    # Get the folder
    folder = (
        await session.exec(
            select(Folder)
            .where(Folder.id == folder_id)
        )
    ).first()

    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # If folder belongs to the user directly, they have full access
    if folder.user_id == user_id:
        return True

    # If folder has a workspace, check workspace permissions
    if folder.workspace_id:
        return await verify_workspace_access(
            session=session,
            workspace_id=folder.workspace_id,
            user_id=user_id,
            required_role=required_role,
        )

    # If folder doesn't have a workspace and doesn't belong to the user, deny access
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Folder not found or access denied",
    )
