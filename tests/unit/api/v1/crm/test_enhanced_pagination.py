"""Unit tests for enhanced pagination utility function."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel import select

from langflow.api.v1.crm.utils import paginate_query
from langflow.api.v1.crm.models import PaginationMetadata
from langflow.services.database.models.crm.client import Client


@pytest.mark.asyncio
class TestEnhancedPaginateQuery:
    """Tests for the enhanced paginate_query function."""
    
    async def test_paginate_query_with_session(self):
        """Test paginate_query with session parameter."""
        # Create a mock session
        mock_session = AsyncMock()
        mock_exec_result = AsyncMock()
        mock_exec_result.one.return_value = 100  # Total count
        mock_exec_result.all.return_value = ["item1", "item2", "item3"]  # Items
        mock_session.exec.return_value = mock_exec_result
        
        # Create a base query
        query = select(Client)
        
        # Apply pagination
        items, metadata = await paginate_query(
            session=mock_session,
            query=query,
            skip=10,
            limit=20
        )
        
        # Check that the session.exec was called twice
        assert mock_session.exec.call_count == 2
        
        # Check the returned items
        assert items == ["item1", "item2", "item3"]
        
        # Check the metadata
        assert isinstance(metadata, PaginationMetadata)
        assert metadata.total == 100
        assert metadata.page == 1
        assert metadata.size == 20
        assert metadata.pages == 5
        assert metadata.has_next is True
        assert metadata.has_prev is False
        assert metadata.next_page == 2
        assert metadata.prev_page is None
    
    async def test_paginate_query_with_page_parameter(self):
        """Test paginate_query with page parameter."""
        # Create a mock session
        mock_session = AsyncMock()
        mock_exec_result = AsyncMock()
        mock_exec_result.one.return_value = 100  # Total count
        mock_exec_result.all.return_value = ["item1", "item2", "item3"]  # Items
        mock_session.exec.return_value = mock_exec_result
        
        # Create a base query
        query = select(Client)
        
        # Apply pagination with page parameter
        items, metadata = await paginate_query(
            session=mock_session,
            query=query,
            page=3,
            limit=10
        )
        
        # Check that the session.exec was called twice
        assert mock_session.exec.call_count == 2
        
        # Check the returned items
        assert items == ["item1", "item2", "item3"]
        
        # Check the metadata
        assert isinstance(metadata, PaginationMetadata)
        assert metadata.total == 100
        assert metadata.page == 3
        assert metadata.size == 10
        assert metadata.pages == 10
        assert metadata.has_next is True
        assert metadata.has_prev is True
        assert metadata.next_page == 4
        assert metadata.prev_page == 2
    
    async def test_paginate_query_last_page(self):
        """Test paginate_query with last page."""
        # Create a mock session
        mock_session = AsyncMock()
        mock_exec_result = AsyncMock()
        mock_exec_result.one.return_value = 100  # Total count
        mock_exec_result.all.return_value = ["item1", "item2", "item3"]  # Items
        mock_session.exec.return_value = mock_exec_result
        
        # Create a base query
        query = select(Client)
        
        # Apply pagination with last page
        items, metadata = await paginate_query(
            session=mock_session,
            query=query,
            page=10,
            limit=10
        )
        
        # Check the metadata
        assert isinstance(metadata, PaginationMetadata)
        assert metadata.total == 100
        assert metadata.page == 10
        assert metadata.size == 10
        assert metadata.pages == 10
        assert metadata.has_next is False
        assert metadata.has_prev is True
        assert metadata.next_page is None
        assert metadata.prev_page == 9
    
    async def test_paginate_query_with_zero_results(self):
        """Test paginate_query with zero results."""
        # Create a mock session
        mock_session = AsyncMock()
        mock_exec_result = AsyncMock()
        mock_exec_result.one.return_value = 0  # Total count
        mock_exec_result.all.return_value = []  # Items
        mock_session.exec.return_value = mock_exec_result
        
        # Create a base query
        query = select(Client)
        
        # Apply pagination
        items, metadata = await paginate_query(
            session=mock_session,
            query=query,
            skip=0,
            limit=10
        )
        
        # Check the returned items
        assert items == []
        
        # Check the metadata
        assert isinstance(metadata, PaginationMetadata)
        assert metadata.total == 0
        assert metadata.page == 1
        assert metadata.size == 10
        assert metadata.pages == 1
        assert metadata.has_next is False
        assert metadata.has_prev is False
        assert metadata.next_page is None
        assert metadata.prev_page is None
