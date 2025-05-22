# Workspace Hierarchy Implementation Plan

## Overview

This document outlines the implementation plan for adding a "Workspace" feature to Langflow's hierarchy structure. Currently, the system has a two-level hierarchy where users create projects (folders) and then flows under those projects. The new feature will add a third level at the top of this hierarchy:

1. Workspace (NEW top level)
2. Projects (existing middle level)
3. Flows (existing bottom level)

## Current Architecture Analysis

### Database Schema

The current database schema consists of the following main entities:

1. **User**
   - Has many Folders (Projects)
   - Has many Flows
   - Has many API Keys
   - Has many Variables

2. **Folder (Project)**
   - Belongs to a User
   - Has many Flows
   - Can have a parent Folder (hierarchical structure)
   - Has many child Folders

3. **Flow**
   - Belongs to a User
   - Can belong to a Folder
   - Contains the actual flow data

### Entity Relationships

- A User can have multiple Folders and Flows
- A Folder can have multiple child Folders and Flows
- A Flow belongs to a User and optionally to a Folder

## Implementation Plan

### 1. Database Schema Modifications

#### 1.1 Create Workspace Model

```python
class WorkspaceBase(SQLModel):
    name: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))

class Workspace(WorkspaceBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    owner_id: UUID = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="owned_workspaces")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    folders: list["Folder"] = Relationship(back_populates="workspace")
    members: list["WorkspaceMember"] = Relationship(back_populates="workspace")

class WorkspaceMember(SQLModel, table=True):
    workspace_id: UUID = Field(foreign_key="workspace.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role: str = Field(default="viewer")  # Options: owner, editor, viewer
    workspace: Workspace = Relationship(back_populates="members")
    user: User = Relationship(back_populates="workspace_memberships")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceRead(WorkspaceBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

class WorkspaceUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
```

#### 1.2 Update User Model

```python
class User(SQLModel, table=True):
    # Existing fields...
    owned_workspaces: list["Workspace"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "delete"},
    )
    workspace_memberships: list["WorkspaceMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "delete"},
    )
```

#### 1.3 Update Folder Model

```python
class Folder(FolderBase, table=True):
    # Existing fields...
    workspace_id: UUID | None = Field(default=None, foreign_key="workspace.id", nullable=True, index=True)
    workspace: Optional["Workspace"] = Relationship(back_populates="folders")
    
    # Update table constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name", "workspace_id", name="unique_folder_name_per_workspace"),
    )
```

### 2. API Endpoint Changes

#### 2.1 Create Workspace Endpoints

```python
@router.post("/workspaces/", response_model=WorkspaceRead, status_code=201)
async def create_workspace(
    *,
    session: DbSession,
    workspace: WorkspaceCreate,
    current_user: CurrentActiveUser,
):
    """Create a new workspace."""
    db_workspace = Workspace(
        **workspace.model_dump(),
        owner_id=current_user.id,
    )
    
    # Add the creator as an owner member
    workspace_member = WorkspaceMember(
        workspace_id=db_workspace.id,
        user_id=current_user.id,
        role="owner"
    )
    
    session.add(db_workspace)
    session.add(workspace_member)
    await session.commit()
    await session.refresh(db_workspace)
    return db_workspace

@router.get("/workspaces/", response_model=list[WorkspaceRead], status_code=200)
async def read_workspaces(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
):
    """Get all workspaces the user has access to."""
    # Get workspaces where user is owner or member
    workspaces = (
        await session.exec(
            select(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(
                or_(
                    Workspace.owner_id == current_user.id,
                    WorkspaceMember.user_id == current_user.id
                )
            )
        )
    ).all()
    return workspaces

@router.get("/workspaces/{workspace_id}", response_model=WorkspaceRead, status_code=200)
async def read_workspace(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific workspace."""
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
    
    if not workspace_member and not (
        await session.exec(
            select(Workspace)
            .where(
                Workspace.id == workspace_id,
                Workspace.owner_id == current_user.id
            )
        )
    ).first():
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
    
    workspace = (
        await session.exec(
            select(Workspace)
            .where(Workspace.id == workspace_id)
        )
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return workspace
```

#### 2.2 Update Project Endpoints

```python
@router.post("/projects/", response_model=FolderRead, status_code=201)
async def create_project(
    *,
    session: DbSession,
    project: FolderCreate,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
):
    """Create a new project in a workspace."""
    # If workspace_id is provided, check if user has access
    if workspace_id:
        workspace_member = (
            await session.exec(
                select(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == current_user.id
                )
            )
        ).first()
        
        if not workspace_member and not (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    Workspace.owner_id == current_user.id
                )
            )
        ).first():
            raise HTTPException(status_code=404, detail="Workspace not found or access denied")
    
    db_project = Folder(
        **project.model_dump(),
        user_id=current_user.id,
        workspace_id=workspace_id,
    )
    
    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)
    return db_project

@router.get("/projects/", response_model=list[FolderRead], status_code=200)
async def read_projects(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
):
    """Get all projects in a workspace."""
    # If workspace_id is provided, check if user has access
    if workspace_id:
        workspace_member = (
            await session.exec(
                select(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == current_user.id
                )
            )
        ).first()
        
        if not workspace_member and not (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    Workspace.owner_id == current_user.id
                )
            )
        ).first():
            raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
        projects = (
            await session.exec(
                select(Folder)
                .where(
                    Folder.workspace_id == workspace_id
                )
            )
        ).all()
    else:
        # Get personal projects (not in any workspace)
        projects = (
            await session.exec(
                select(Folder)
                .where(
                    Folder.user_id == current_user.id,
                    Folder.workspace_id == None  # noqa: E711
                )
            )
        ).all()
    
    return projects
```

### 3. UI/UX Considerations

#### 3.1 Frontend Models

```typescript
// New Workspace Type
export type WorkspaceType = {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
};

// Update FolderType to include workspace_id
export type FolderType = {
  name: string;
  description: string;
  id?: string | null;
  parent_id: string;
  workspace_id?: string | null;
  flows: FlowType[];
  components: string[];
};
```

#### 3.2 UI Components

1. **Workspace Selector**
   - Add a dropdown in the header to select the current workspace
   - Show personal workspace by default
   - Allow switching between workspaces

2. **Workspace Management**
   - Create a new workspace management page
   - List all workspaces the user has access to
   - Allow creating, editing, and deleting workspaces
   - Manage workspace members and permissions

3. **Project Sidebar**
   - Update the sidebar to show projects within the selected workspace
   - Add visual indicators for workspace ownership/membership

4. **Navigation Structure**
   - Update URL structure to include workspace ID: `/workspace/{workspace_id}/folder/{folder_id}/flow/{flow_id}`
   - Update breadcrumb navigation to show workspace > project > flow

### 4. Permission Model

#### 4.1 Workspace Roles

1. **Owner**
   - Full control over the workspace
   - Can add/remove members
   - Can create/edit/delete projects and flows
   - Can change workspace settings

2. **Editor**
   - Can create/edit/delete projects and flows
   - Cannot add/remove members
   - Cannot change workspace settings

3. **Viewer**
   - Can view projects and flows
   - Cannot create/edit/delete anything

#### 4.2 Permission Checks

- Add permission checks to all API endpoints that interact with workspaces, projects, or flows
- Implement middleware to verify workspace access
- Update frontend to show/hide actions based on user permissions

### 5. Migration Strategy

#### 5.1 Database Migration

1. Create a new Alembic migration script:
   ```python
   # Create workspace table
   op.create_table(
       "workspace",
       sa.Column("id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
       sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
       sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
       sa.Column("owner_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
       sa.Column("created_at", sa.DateTime(), nullable=False),
       sa.Column("updated_at", sa.DateTime(), nullable=False),
       sa.ForeignKeyConstraint(["owner_id"], ["user.id"]),
       sa.PrimaryKeyConstraint("id"),
   )
   
   # Create workspace_member table
   op.create_table(
       "workspace_member",
       sa.Column("workspace_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
       sa.Column("user_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
       sa.Column("role", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
       sa.Column("created_at", sa.DateTime(), nullable=False),
       sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]),
       sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
       sa.PrimaryKeyConstraint("workspace_id", "user_id"),
   )
   
   # Add workspace_id to folder table
   op.add_column("folder", sa.Column("workspace_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=True))
   op.create_foreign_key(None, "folder", "workspace", ["workspace_id"], ["id"])
   
   # Update unique constraint on folder table
   op.drop_constraint("unique_folder_name", "folder")
   op.create_unique_constraint("unique_folder_name_per_workspace", "folder", ["user_id", "name", "workspace_id"])
   ```

#### 5.2 Data Migration

1. Create a "Personal" workspace for each existing user
2. Migrate existing projects to the personal workspace
3. Ensure all relationships are maintained

```python
# Create personal workspaces for existing users
users = session.exec(select(User)).all()
for user in users:
    personal_workspace = Workspace(
        name="Personal",
        description="Your personal workspace",
        owner_id=user.id,
    )
    session.add(personal_workspace)
    session.commit()
    session.refresh(personal_workspace)
    
    # Add user as owner of their personal workspace
    workspace_member = WorkspaceMember(
        workspace_id=personal_workspace.id,
        user_id=user.id,
        role="owner"
    )
    session.add(workspace_member)
    
    # Migrate existing folders to personal workspace
    folders = session.exec(select(Folder).where(Folder.user_id == user.id)).all()
    for folder in folders:
        folder.workspace_id = personal_workspace.id
    
    session.commit()
```

## Implementation Timeline

1. **Phase 1: Database Schema Changes (Week 1)**
   - Create workspace and workspace_member tables
   - Update folder table with workspace_id
   - Create migration scripts

2. **Phase 2: Backend API Implementation (Week 2)**
   - Implement workspace CRUD endpoints
   - Update project endpoints to work with workspaces
   - Implement permission checks

3. **Phase 3: Frontend Implementation (Week 3)**
   - Create workspace management UI
   - Update project sidebar and navigation
   - Implement workspace selector

4. **Phase 4: Testing and Refinement (Week 4)**
   - Test all functionality
   - Fix bugs and edge cases
   - Optimize performance

5. **Phase 5: Documentation and Deployment (Week 5)**
   - Update API documentation
   - Create user guides
   - Deploy to production

## Conclusion

This implementation plan provides a comprehensive approach to adding a workspace feature to Langflow's hierarchy structure. By following this plan, we can create a robust multi-level hierarchy that allows for better organization and collaboration while minimizing disruption to existing functionality.
