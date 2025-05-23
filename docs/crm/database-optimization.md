# CRM Module Database Optimization

This document outlines the database optimization techniques applied to the CRM module in Langflow.

## Foreign Key Relationship Best Practices

### String References for Foreign Keys

When defining foreign key relationships in SQLModel/SQLAlchemy, use string references without square brackets:

```python
# CORRECT
creator: "User" = Relationship(
    back_populates="created_clients", 
    sa_relationship_kwargs={"foreign_keys": "Client.created_by"}
)

# INCORRECT
creator: "User" = Relationship(
    back_populates="created_clients", 
    sa_relationship_kwargs={"foreign_keys": "[Client.created_by]"}
)
```

### Proper Indexing

Always set `index=True` for foreign key fields to improve query performance:

```python
workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
created_by: UUIDstr = Field(index=True, foreign_key="user.id")
```

## Query Optimization Techniques

### Consolidating Multiple Queries

Instead of making multiple separate queries, use SQL aggregation functions to get multiple metrics in a single query:

```python
# OPTIMIZED: Single query with multiple aggregations
client_stats = (
    await session.exec(
        select(
            func.count().label("total_count"),
            func.sum(case((Client.status == "active", 1), else_=0)).label("active_count")
        )
        .where(Client.workspace_id == workspace_id)
    )
).one()

# UNOPTIMIZED: Multiple separate queries
client_count = (
    await session.exec(
        select(func.count())
        .where(Client.workspace_id == workspace_id)
    )
).one()

active_client_count = (
    await session.exec(
        select(func.count())
        .where(
            Client.workspace_id == workspace_id,
            Client.status == "active"
        )
    )
).one()
```

### Using GROUP BY for Distribution Queries

For distribution queries, use a single query with GROUP BY instead of multiple separate queries:

```python
# OPTIMIZED: Single query with GROUP BY
status_counts = (
    await session.exec(
        select(
            Client.status,
            func.count().label("count")
        )
        .where(Client.workspace_id == workspace_id)
        .group_by(Client.status)
    )
).all()

# UNOPTIMIZED: Multiple separate queries for each status
active_clients = (
    await session.exec(
        select(func.count())
        .where(
            Client.workspace_id == workspace_id,
            Client.status == "active"
        )
    )
).one()

inactive_clients = (
    await session.exec(
        select(func.count())
        .where(
            Client.workspace_id == workspace_id,
            Client.status == "inactive"
        )
    )
).one()
```

## Code Organization

### Reusable Functions for Common Operations

Extract common operations into reusable functions to reduce code duplication:

```python
async def check_workspace_access(session: DbSession, workspace_id: UUID, current_user: CurrentActiveUser):
    """Check if the user has access to the workspace and return the workspace if they do."""
    workspace = (
        await session.exec(
            select(Workspace)
            .where(
                Workspace.id == workspace_id,
                or_(
                    Workspace.owner_id == current_user.id,
                    Workspace.id.in_(
                        select(WorkspaceMember.workspace_id)
                        .where(WorkspaceMember.user_id == current_user.id)
                    )
                )
            )
        )
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )
    
    return workspace
```

## UUID Handling

### PostgreSQL-Specific UUID Column Type

For PostgreSQL databases, use the PostgreSQL-specific UUID column type:

```python
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

id: UUIDstr = Field(
    default_factory=uuid4,
    primary_key=True,
    sa_column=Column(PostgresUUID(as_uuid=True), unique=True)
)
```

## Testing

Unit tests have been added to verify the proper functioning of the CRM database models and their relationships. These tests ensure that:

1. Models can be created successfully
2. Foreign key relationships are properly enforced
3. Relationships between models work as expected

Run the tests with:

```bash
pytest src/backend/base/langflow/tests/unit/test_crm_models.py -v
```
