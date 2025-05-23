"""Unit tests for pagination utility function."""
import pytest
from sqlmodel import select

from langflow.api.v1.crm.utils import paginate_query
from langflow.services.database.models.crm.client import Client


class TestPaginateQuery:
    """Tests for the paginate_query function."""
    
    def test_paginate_query_default_values(self):
        """Test paginate_query with default values."""
        # Create a base query
        query = select(Client)
        
        # Apply pagination with default values
        paginated_query = paginate_query(query)
        
        # Check that the query has offset and limit clauses
        query_str = str(paginated_query)
        assert "OFFSET" in query_str
        assert "LIMIT" in query_str
        assert "OFFSET 0" in query_str
        assert "LIMIT 100" in query_str
    
    def test_paginate_query_custom_values(self):
        """Test paginate_query with custom values."""
        # Create a base query
        query = select(Client)
        
        # Apply pagination with custom values
        paginated_query = paginate_query(query, skip=10, limit=20)
        
        # Check that the query has offset and limit clauses
        query_str = str(paginated_query)
        assert "OFFSET" in query_str
        assert "LIMIT" in query_str
        assert "OFFSET 10" in query_str
        assert "LIMIT 20" in query_str
    
    def test_paginate_query_with_where_clause(self):
        """Test paginate_query with a query that has a where clause."""
        # Create a base query with a where clause
        query = select(Client).where(Client.status == "active")
        
        # Apply pagination
        paginated_query = paginate_query(query, skip=5, limit=10)
        
        # Check that the query has where, offset, and limit clauses
        query_str = str(paginated_query)
        assert "WHERE" in query_str
        assert "status" in query_str
        assert "active" in query_str
        assert "OFFSET 5" in query_str
        assert "LIMIT 10" in query_str
    
    def test_paginate_query_with_order_by(self):
        """Test paginate_query with a query that has an order by clause."""
        # Create a base query with an order by clause
        query = select(Client).order_by(Client.name)
        
        # Apply pagination
        paginated_query = paginate_query(query, skip=0, limit=50)
        
        # Check that the query has order by, offset, and limit clauses
        query_str = str(paginated_query)
        assert "ORDER BY" in query_str
        assert "name" in query_str
        assert "OFFSET 0" in query_str
        assert "LIMIT 50" in query_str
    
    def test_paginate_query_with_zero_limit(self):
        """Test paginate_query with a limit of zero."""
        # Create a base query
        query = select(Client)
        
        # Apply pagination with a limit of zero
        paginated_query = paginate_query(query, skip=0, limit=0)
        
        # Check that the query has offset and limit clauses
        query_str = str(paginated_query)
        assert "OFFSET 0" in query_str
        assert "LIMIT 0" in query_str
    
    def test_paginate_query_with_negative_skip(self):
        """Test paginate_query with a negative skip value."""
        # Create a base query
        query = select(Client)
        
        # Apply pagination with a negative skip value
        # This should be treated as 0
        paginated_query = paginate_query(query, skip=-10, limit=10)
        
        # Check that the query has offset and limit clauses
        query_str = str(paginated_query)
        assert "OFFSET 0" in query_str  # Should be 0, not -10
        assert "LIMIT 10" in query_str
    
    def test_paginate_query_with_negative_limit(self):
        """Test paginate_query with a negative limit value."""
        # Create a base query
        query = select(Client)
        
        # Apply pagination with a negative limit value
        # This should be treated as 0
        paginated_query = paginate_query(query, skip=0, limit=-10)
        
        # Check that the query has offset and limit clauses
        query_str = str(paginated_query)
        assert "OFFSET 0" in query_str
        assert "LIMIT 0" in query_str  # Should be 0, not -10
