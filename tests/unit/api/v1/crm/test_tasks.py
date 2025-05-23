"""Unit tests for CRM task endpoints."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlmodel import select

from langflow.api.v1.crm.tasks import (
    create_task,
    read_tasks,
    read_task,
    update_task,
    delete_task,
)
from langflow.services.database.models.crm.task import (
    Task,
    TaskCreate,
    TaskUpdate,
)


class TestCreateTask:
    """Tests for the create_task endpoint."""

    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.tasks.check_workspace_access")
    @patch("langflow.api.v1.crm.tasks.update_entity_timestamps")
    async def test_create_task_success(
        self, mock_update_timestamps, mock_check_access
    ):
        """Test successful task creation."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock task data
        task_data = TaskCreate(
            title="Test Task",
            workspace_id=uuid.uuid4(),
            client_id=uuid.uuid4(),
            status="open",
            priority="medium",
        )
        
        # Mock check_workspace_access
        mock_check_access.return_value = MagicMock()
        
        # Call function
        result = await create_task(
            session=session,
            task=task_data,
            current_user=current_user,
        )
        
        # Assert
        assert result is not None
        assert result.title == "Test Task"
        assert result.created_by == current_user.id
        mock_check_access.assert_called_once_with(
            session,
            task_data.workspace_id,
            current_user,
            require_edit_permission=True
        )
        mock_update_timestamps.assert_called_once()
        session.add.assert_called_once()
        session.commit.assert_called_once()
        session.refresh.assert_called_once()
        
    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.tasks.check_workspace_access")
    async def test_create_task_no_access(self, mock_check_access):
        """Test task creation with no workspace access."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock task data
        task_data = TaskCreate(
            title="Test Task",
            workspace_id=uuid.uuid4(),
            client_id=uuid.uuid4(),
            status="open",
            priority="medium",
        )
        
        # Mock check_workspace_access to raise exception
        mock_check_access.side_effect = HTTPException(
            status_code=404,
            detail="Workspace not found or you don't have edit permission",
        )
        
        # Call function and assert exception
        with pytest.raises(HTTPException) as excinfo:
            await create_task(
                session=session,
                task=task_data,
                current_user=current_user,
            )
        
        # Assert
        assert excinfo.value.status_code == 404
        assert "Workspace not found" in excinfo.value.detail
        mock_check_access.assert_called_once()
        session.add.assert_not_called()
        session.commit.assert_not_called()


class TestReadTasks:
    """Tests for the read_tasks endpoint."""

    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.tasks.get_entity_access_filter")
    async def test_read_tasks_success(self, mock_get_filter):
        """Test successful tasks retrieval."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock filter
        mock_get_filter.return_value = MagicMock()
        
        # Mock tasks
        task1 = MagicMock()
        task1.id = uuid.uuid4()
        task1.title = "Task 1"
        
        task2 = MagicMock()
        task2.id = uuid.uuid4()
        task2.title = "Task 2"
        
        # Mock session.exec to return tasks
        session.exec.return_value.all.return_value = [task1, task2]
        
        # Call function
        result = await read_tasks(
            session=session,
            current_user=current_user,
        )
        
        # Assert
        assert len(result) == 2
        assert result[0].title == "Task 1"
        assert result[1].title == "Task 2"
        mock_get_filter.assert_called_once_with(Task, current_user.id)
        session.exec.assert_called_once()


class TestUpdateTask:
    """Tests for the update_task endpoint."""

    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.tasks.check_workspace_access")
    @patch("langflow.api.v1.crm.tasks.update_entity_timestamps")
    async def test_update_task_success(
        self, mock_update_timestamps, mock_check_access
    ):
        """Test successful task update."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock task ID
        task_id = uuid.uuid4()
        
        # Mock task data
        task_data = TaskUpdate(
            title="Updated Task",
            status="completed",
        )
        
        # Mock existing task
        db_task = MagicMock()
        db_task.id = task_id
        db_task.title = "Original Task"
        db_task.workspace_id = uuid.uuid4()
        
        # Mock session.exec to return task
        session.exec.return_value.first.return_value = db_task
        
        # Mock check_workspace_access
        mock_check_access.return_value = MagicMock()
        
        # Call function
        result = await update_task(
            session=session,
            task_id=task_id,
            task=task_data,
            current_user=current_user,
        )
        
        # Assert
        assert result is not None
        assert result.id == task_id
        mock_check_access.assert_called_once_with(
            session,
            db_task.workspace_id,
            current_user,
            require_edit_permission=True
        )
        mock_update_timestamps.assert_called_once()
        session.commit.assert_called_once()
        session.refresh.assert_called_once()


class TestDeleteTask:
    """Tests for the delete_task endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task_as_creator(self):
        """Test task deletion by creator."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock task ID
        task_id = uuid.uuid4()
        
        # Mock existing task
        db_task = MagicMock()
        db_task.id = task_id
        db_task.created_by = current_user.id
        db_task.workspace_id = uuid.uuid4()
        
        # Mock session.exec to return task
        session.exec.return_value.first.return_value = db_task
        
        # Call function
        result = await delete_task(
            session=session,
            task_id=task_id,
            current_user=current_user,
        )
        
        # Assert
        assert result is None
        session.delete.assert_called_once_with(db_task)
        session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.tasks.check_workspace_access")
    async def test_delete_task_as_workspace_owner(self, mock_check_access):
        """Test task deletion by workspace owner."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock task ID
        task_id = uuid.uuid4()
        
        # Mock existing task
        db_task = MagicMock()
        db_task.id = task_id
        db_task.created_by = uuid.uuid4()  # Different from current_user.id
        db_task.workspace_id = uuid.uuid4()
        
        # Mock session.exec to return task
        session.exec.return_value.first.return_value = db_task
        
        # Mock check_workspace_access
        mock_check_access.return_value = MagicMock()
        
        # Call function
        result = await delete_task(
            session=session,
            task_id=task_id,
            current_user=current_user,
        )
        
        # Assert
        assert result is None
        mock_check_access.assert_called_once_with(
            session,
            db_task.workspace_id,
            current_user,
            require_owner_permission=True
        )
        session.delete.assert_called_once_with(db_task)
        session.commit.assert_called_once()
