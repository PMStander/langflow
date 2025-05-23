from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.workspace import (
    Workspace,
    WorkspaceMember,
    WorkspaceMemberCreate,
    WorkspaceMemberRead,
    WorkspaceMemberUpdate,
)

router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["Workspace Members"])


@router.post("/", response_model=WorkspaceMemberRead, status_code=201)
async def add_workspace_member(
    *,
    session: DbSession,
    workspace_id: UUID,
    member: WorkspaceMemberCreate,
    current_user: CurrentActiveUser,
):
    """Add a member to a workspace."""
    try:
        # Check if user is the owner of the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    Workspace.owner_id == current_user.id
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you don't have permission to add members",
            )
        
        # Check if the member already exists
        existing_member = (
            await session.exec(
                select(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == member.user_id
                )
            )
        ).first()
        
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this workspace",
            )
        
        # Create the workspace member
        db_member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=member.user_id,
            role=member.role,
        )
        session.add(db_member)
        await session.commit()
        await session.refresh(db_member)
        
        return db_member
    except HTTPException:
        raise
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID or workspace ID",
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/", response_model=list[WorkspaceMemberRead], status_code=200)
async def read_workspace_members(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get all members of a workspace."""
    try:
        # Check if user has access to this workspace
        workspace_member = (
            await session.exec(
                select(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == current_user.id
                )
            )
        ).first()
        
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                )
            )
        ).first()
        
        if not workspace or (not workspace_member and workspace.owner_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )
        
        # Get all members of the workspace
        members = (
            await session.exec(
                select(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id
                )
            )
        ).all()
        
        return members
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{user_id}", response_model=WorkspaceMemberRead, status_code=200)
async def update_workspace_member(
    *,
    session: DbSession,
    workspace_id: UUID,
    user_id: UUID,
    member: WorkspaceMemberUpdate,
    current_user: CurrentActiveUser,
):
    """Update a workspace member's role."""
    try:
        # Check if user is the owner of the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    Workspace.owner_id == current_user.id
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you don't have permission to update members",
            )
        
        # Get the member to update
        db_member = (
            await session.exec(
                select(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id
                )
            )
        ).first()
        
        if not db_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found in this workspace",
            )
        
        # Update member fields
        member_data = member.model_dump(exclude_unset=True)
        for key, value in member_data.items():
            setattr(db_member, key, value)
        
        await session.commit()
        await session.refresh(db_member)
        
        return db_member
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{user_id}", status_code=204)
async def remove_workspace_member(
    *,
    session: DbSession,
    workspace_id: UUID,
    user_id: UUID,
    current_user: CurrentActiveUser,
):
    """Remove a member from a workspace."""
    try:
        # Check if user is the owner of the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    Workspace.owner_id == current_user.id
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you don't have permission to remove members",
            )
        
        # Get the member to remove
        db_member = (
            await session.exec(
                select(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id
                )
            )
        ).first()
        
        if not db_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found in this workspace",
            )
        
        # Cannot remove the owner
        if user_id == workspace.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the workspace owner",
            )
        
        # Remove the member
        await session.delete(db_member)
        await session.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
