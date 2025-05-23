"""Unit tests for CRM opportunity endpoints."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlmodel import select

from langflow.api.v1.crm.opportunities import (
    create_opportunity,
    read_opportunities,
    read_opportunity,
    update_opportunity,
    delete_opportunity,
)
from langflow.services.database.models.crm.opportunity import (
    Opportunity,
    OpportunityCreate,
    OpportunityUpdate,
)


class TestCreateOpportunity:
    """Tests for the create_opportunity endpoint."""

    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.opportunities.check_workspace_access")
    @patch("langflow.api.v1.crm.opportunities.update_entity_timestamps")
    async def test_create_opportunity_success(
        self, mock_update_timestamps, mock_check_access
    ):
        """Test successful opportunity creation."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock opportunity data
        opportunity_data = OpportunityCreate(
            name="Test Opportunity",
            workspace_id=uuid.uuid4(),
            client_id=uuid.uuid4(),
            value=1000.0,
            status="open",
        )
        
        # Mock check_workspace_access
        mock_check_access.return_value = MagicMock()
        
        # Call function
        result = await create_opportunity(
            session=session,
            opportunity=opportunity_data,
            current_user=current_user,
        )
        
        # Assert
        assert result is not None
        assert result.name == "Test Opportunity"
        assert result.created_by == current_user.id
        mock_check_access.assert_called_once_with(
            session,
            opportunity_data.workspace_id,
            current_user,
            require_edit_permission=True
        )
        mock_update_timestamps.assert_called_once()
        session.add.assert_called_once()
        session.commit.assert_called_once()
        session.refresh.assert_called_once()
        
    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.opportunities.check_workspace_access")
    async def test_create_opportunity_no_access(self, mock_check_access):
        """Test opportunity creation with no workspace access."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock opportunity data
        opportunity_data = OpportunityCreate(
            name="Test Opportunity",
            workspace_id=uuid.uuid4(),
            client_id=uuid.uuid4(),
            value=1000.0,
            status="open",
        )
        
        # Mock check_workspace_access to raise exception
        mock_check_access.side_effect = HTTPException(
            status_code=404,
            detail="Workspace not found or you don't have edit permission",
        )
        
        # Call function and assert exception
        with pytest.raises(HTTPException) as excinfo:
            await create_opportunity(
                session=session,
                opportunity=opportunity_data,
                current_user=current_user,
            )
        
        # Assert
        assert excinfo.value.status_code == 404
        assert "Workspace not found" in excinfo.value.detail
        mock_check_access.assert_called_once()
        session.add.assert_not_called()
        session.commit.assert_not_called()


class TestReadOpportunities:
    """Tests for the read_opportunities endpoint."""

    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.opportunities.get_entity_access_filter")
    async def test_read_opportunities_success(self, mock_get_filter):
        """Test successful opportunities retrieval."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock filter
        mock_get_filter.return_value = MagicMock()
        
        # Mock opportunities
        opportunity1 = MagicMock()
        opportunity1.id = uuid.uuid4()
        opportunity1.name = "Opportunity 1"
        
        opportunity2 = MagicMock()
        opportunity2.id = uuid.uuid4()
        opportunity2.name = "Opportunity 2"
        
        # Mock session.exec to return opportunities
        session.exec.return_value.all.return_value = [opportunity1, opportunity2]
        
        # Call function
        result = await read_opportunities(
            session=session,
            current_user=current_user,
        )
        
        # Assert
        assert len(result) == 2
        assert result[0].name == "Opportunity 1"
        assert result[1].name == "Opportunity 2"
        mock_get_filter.assert_called_once_with(Opportunity, current_user.id)
        session.exec.assert_called_once()


class TestReadOpportunity:
    """Tests for the read_opportunity endpoint."""

    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.opportunities.get_entity_access_filter")
    async def test_read_opportunity_success(self, mock_get_filter):
        """Test successful opportunity retrieval."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock opportunity ID
        opportunity_id = uuid.uuid4()
        
        # Mock filter
        mock_get_filter.return_value = MagicMock()
        
        # Mock opportunity
        opportunity = MagicMock()
        opportunity.id = opportunity_id
        opportunity.name = "Test Opportunity"
        
        # Mock session.exec to return opportunity
        session.exec.return_value.first.return_value = opportunity
        
        # Call function
        result = await read_opportunity(
            session=session,
            opportunity_id=opportunity_id,
            current_user=current_user,
        )
        
        # Assert
        assert result is not None
        assert result.id == opportunity_id
        assert result.name == "Test Opportunity"
        mock_get_filter.assert_called_once_with(Opportunity, current_user.id)
        session.exec.assert_called_once()
        
    @pytest.mark.asyncio
    @patch("langflow.api.v1.crm.opportunities.get_entity_access_filter")
    async def test_read_opportunity_not_found(self, mock_get_filter):
        """Test opportunity retrieval when not found."""
        # Mock session and user
        session = AsyncMock()
        current_user = MagicMock()
        current_user.id = uuid.uuid4()
        
        # Mock opportunity ID
        opportunity_id = uuid.uuid4()
        
        # Mock filter
        mock_get_filter.return_value = MagicMock()
        
        # Mock session.exec to return None
        session.exec.return_value.first.return_value = None
        
        # Call function and assert exception
        with pytest.raises(HTTPException) as excinfo:
            await read_opportunity(
                session=session,
                opportunity_id=opportunity_id,
                current_user=current_user,
            )
        
        # Assert
        assert excinfo.value.status_code == 404
        assert "Opportunity not found or access denied" in excinfo.value.detail
        mock_get_filter.assert_called_once_with(Opportunity, current_user.id)
        session.exec.assert_called_once()
