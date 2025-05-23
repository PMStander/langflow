"""Unit tests for CRM database models."""
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.exc import IntegrityError

from langflow.services.database.models.user import User
from langflow.services.database.models.workspace import Workspace
from langflow.services.database.models.crm.client import Client
from langflow.services.database.models.crm.invoice import Invoice
from langflow.services.database.models.crm.opportunity import Opportunity
from langflow.services.database.models.crm.task import Task


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_user(in_memory_db):
    """Create a test user."""
    user = User(
        id=str(uuid4()),
        username="testuser",
        password="password",
        is_active=True,
        is_superuser=False,
        create_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(user)
    in_memory_db.commit()
    in_memory_db.refresh(user)
    return user


@pytest.fixture
def test_workspace(in_memory_db, test_user):
    """Create a test workspace."""
    workspace = Workspace(
        id=str(uuid4()),
        name="Test Workspace",
        description="Test workspace description",
        owner_id=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(workspace)
    in_memory_db.commit()
    in_memory_db.refresh(workspace)
    return workspace


def test_client_model_creation(in_memory_db, test_user, test_workspace):
    """Test creating a client model."""
    client = Client(
        id=str(uuid4()),
        name="Test Client",
        email="client@example.com",
        phone="123-456-7890",
        company="Test Company",
        description="Test client description",
        status="active",
        workspace_id=test_workspace.id,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(client)
    in_memory_db.commit()
    in_memory_db.refresh(client)
    
    # Test that the client was created successfully
    assert client.id is not None
    assert client.name == "Test Client"
    assert client.email == "client@example.com"
    assert client.status == "active"
    
    # Test relationships
    assert client.workspace_id == test_workspace.id
    assert client.created_by == test_user.id


def test_invoice_model_creation(in_memory_db, test_user, test_workspace):
    """Test creating an invoice model."""
    # First create a client
    client = Client(
        id=str(uuid4()),
        name="Test Client",
        workspace_id=test_workspace.id,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(client)
    in_memory_db.commit()
    in_memory_db.refresh(client)
    
    # Now create an invoice for this client
    invoice = Invoice(
        id=str(uuid4()),
        invoice_number="INV-001",
        amount=1000.0,
        status="draft",
        issue_date=datetime.now(timezone.utc),
        due_date=datetime.now(timezone.utc),
        description="Test invoice",
        workspace_id=test_workspace.id,
        client_id=client.id,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(invoice)
    in_memory_db.commit()
    in_memory_db.refresh(invoice)
    
    # Test that the invoice was created successfully
    assert invoice.id is not None
    assert invoice.invoice_number == "INV-001"
    assert invoice.amount == 1000.0
    assert invoice.status == "draft"
    
    # Test relationships
    assert invoice.workspace_id == test_workspace.id
    assert invoice.client_id == client.id
    assert invoice.created_by == test_user.id


def test_opportunity_model_creation(in_memory_db, test_user, test_workspace):
    """Test creating an opportunity model."""
    # First create a client
    client = Client(
        id=str(uuid4()),
        name="Test Client",
        workspace_id=test_workspace.id,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(client)
    in_memory_db.commit()
    in_memory_db.refresh(client)
    
    # Now create an opportunity for this client
    opportunity = Opportunity(
        id=str(uuid4()),
        name="Test Opportunity",
        value=5000.0,
        status="new",
        description="Test opportunity description",
        expected_close_date=datetime.now(timezone.utc),
        workspace_id=test_workspace.id,
        client_id=client.id,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(opportunity)
    in_memory_db.commit()
    in_memory_db.refresh(opportunity)
    
    # Test that the opportunity was created successfully
    assert opportunity.id is not None
    assert opportunity.name == "Test Opportunity"
    assert opportunity.value == 5000.0
    assert opportunity.status == "new"
    
    # Test relationships
    assert opportunity.workspace_id == test_workspace.id
    assert opportunity.client_id == client.id
    assert opportunity.created_by == test_user.id


def test_task_model_creation(in_memory_db, test_user, test_workspace):
    """Test creating a task model."""
    # First create a client
    client = Client(
        id=str(uuid4()),
        name="Test Client",
        workspace_id=test_workspace.id,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(client)
    in_memory_db.commit()
    in_memory_db.refresh(client)
    
    # Now create a task
    task = Task(
        id=str(uuid4()),
        title="Test Task",
        description="Test task description",
        status="open",
        priority="medium",
        due_date=datetime.now(timezone.utc),
        workspace_id=test_workspace.id,
        created_by=test_user.id,
        assigned_to=test_user.id,
        client_id=client.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(task)
    in_memory_db.commit()
    in_memory_db.refresh(task)
    
    # Test that the task was created successfully
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.status == "open"
    assert task.priority == "medium"
    
    # Test relationships
    assert task.workspace_id == test_workspace.id
    assert task.created_by == test_user.id
    assert task.assigned_to == test_user.id
    assert task.client_id == client.id


def test_foreign_key_relationships(in_memory_db, test_user, test_workspace):
    """Test that foreign key relationships are properly enforced."""
    # Create a client
    client = Client(
        id=str(uuid4()),
        name="Test Client",
        workspace_id=test_workspace.id,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(client)
    in_memory_db.commit()
    in_memory_db.refresh(client)
    
    # Try to create an invoice with an invalid client_id
    invalid_invoice = Invoice(
        id=str(uuid4()),
        invoice_number="INV-002",
        amount=1000.0,
        status="draft",
        workspace_id=test_workspace.id,
        client_id=str(uuid4()),  # Invalid client_id
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    in_memory_db.add(invalid_invoice)
    
    # This should raise an IntegrityError due to the foreign key constraint
    with pytest.raises(IntegrityError):
        in_memory_db.commit()
    
    # Rollback the transaction
    in_memory_db.rollback()
