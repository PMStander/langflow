"""Unit tests for CRM utility functions."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlmodel import select

from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
    update_entity_timestamps,
)
from langflow.services.database.models.workspace import Workspace, WorkspaceMember
from langflow.services.database.models.crm.client import Client


class TestCheckWorkspaceAccess:
    """Tests for the check_workspace_access function."""

    @pytest.mark.asyncio
    async def test_check_workspace_access_owner(self):
        """Test check_workspace_access when user is workspace owner."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        
        # Mock workspace
        workspace = MagicMock()
        workspace.id = workspace_id
        workspace.owner_id = current_user.id
        
        # Mock session.exec to return workspace
        session.exec.return_value.first.return_value = workspace
        
        # Call function
        result = await check_workspace_access(
            session, workspace_id, current_user
        )
        
        # Assert
        assert result == workspace
        session.exec.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_check_workspace_access_member(self):
        """Test check_workspace_access when user is workspace member."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        
        # Mock workspace
        workspace = MagicMock()
        workspace.id = workspace_id
        workspace.owner_id = uuid.uuid4()  # Different from current_user.id
        
        # Mock session.exec to return workspace
        session.exec.return_value.first.return_value = workspace
        
        # Call function
        result = await check_workspace_access(
            session, workspace_id, current_user
        )
        
        # Assert
        assert result == workspace
        session.exec.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_check_workspace_access_not_found(self):
        """Test check_workspace_access when workspace not found."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        
        # Mock session.exec to return None
        session.exec.return_value.first.return_value = None
        
        # Call function and assert exception
        with pytest.raises(HTTPException) as excinfo:
            await check_workspace_access(
                session, workspace_id, current_user
            )
        
        # Assert
        assert excinfo.value.status_code == 404
        assert "Workspace not found or access denied" in excinfo.value.detail
        session.exec.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_check_workspace_access_require_edit_permission(self):
        """Test check_workspace_access with require_edit_permission=True."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        
        # Mock workspace
        workspace = MagicMock()
        workspace.id = workspace_id
        workspace.owner_id = uuid.uuid4()  # Different from current_user.id
        
        # Mock session.exec to return workspace
        session.exec.return_value.first.return_value = workspace
        
        # Call function
        result = await check_workspace_access(
            session, workspace_id, current_user, require_edit_permission=True
        )
        
        # Assert
        assert result == workspace
        session.exec.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_check_workspace_access_require_owner_permission(self):
        """Test check_workspace_access with require_owner_permission=True."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        
        # Mock workspace
        workspace = MagicMock()
        workspace.id = workspace_id
        workspace.owner_id = current_user.id
        
        # Mock session.exec to return workspace
        session.exec.return_value.first.return_value = workspace
        
        # Call function
        result = await check_workspace_access(
            session, workspace_id, current_user, require_owner_permission=True
        )
        
        # Assert
        assert result == workspace
        session.exec.assert_called_once()


class TestGetEntityAccessFilter:
    """Tests for the get_entity_access_filter function."""
    
    def test_get_entity_access_filter(self):
        """Test get_entity_access_filter function."""
        # Mock user ID
        user_id = uuid.uuid4()
        
        # Call function
        result = get_entity_access_filter(Client, user_id)
        
        # Assert result is a SQLAlchemy filter expression
        assert result is not None
        assert str(result).startswith("(")
        assert "OR" in str(result)
        assert str(user_id) in str(result)


class TestUpdateEntityTimestamps:
    """Tests for the update_entity_timestamps function."""
    
    def test_update_entity_timestamps_new_entity(self):
        """Test update_entity_timestamps for a new entity."""
        # Mock entity
        entity = MagicMock()
        entity.created_at = None
        entity.updated_at = None
        
        # Call function
        result = update_entity_timestamps(entity, is_new=True)
        
        # Assert
        assert result == entity
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)
        
    def test_update_entity_timestamps_existing_entity(self):
        """Test update_entity_timestamps for an existing entity."""
        # Mock entity
        entity = MagicMock()
        entity.created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)
        entity.updated_at = datetime(2023, 1, 1, tzinfo=timezone.utc)
        
        # Call function
        result = update_entity_timestamps(entity)
        
        # Assert
        assert result == entity
        assert entity.created_at == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert entity.updated_at != datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert isinstance(entity.updated_at, datetime)
        
    def test_update_entity_timestamps_with_update_data(self):
        """Test update_entity_timestamps with update_data."""
        # Mock entity
        entity = MagicMock()
        entity.name = "Old Name"
        entity.description = "Old Description"
        entity.updated_at = datetime(2023, 1, 1, tzinfo=timezone.utc)
        
        # Update data
        update_data = {
            "name": "New Name",
            "description": "New Description"
        }
        
        # Call function
        result = update_entity_timestamps(entity, update_data=update_data)
        
        # Assert
        assert result == entity
        assert entity.name == "New Name"
        assert entity.description == "New Description"
        assert entity.updated_at != datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert isinstance(entity.updated_at, datetime)
