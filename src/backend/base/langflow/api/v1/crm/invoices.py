from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.invoice import (
    Invoice,
    InvoiceCreate,
    InvoiceRead,
    InvoiceUpdate,
)
from langflow.services.database.models.workspace import Workspace, WorkspaceMember

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/", response_model=InvoiceRead, status_code=201)
async def create_invoice(
    *,
    session: DbSession,
    invoice: InvoiceCreate,
    current_user: CurrentActiveUser,
):
    """Create a new invoice."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == invoice.workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role.in_(["owner", "editor"])
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you don't have permission to create invoices in it",
            )
        
        # Create the invoice
        db_invoice = Invoice(
            **invoice.model_dump(),
            created_by=current_user.id,
        )
        session.add(db_invoice)
        await session.commit()
        await session.refresh(db_invoice)
        return db_invoice
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create invoice: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/", response_model=list[InvoiceRead], status_code=200)
async def read_invoices(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    client_id: UUID | None = None,
    status: str | None = None,
):
    """Get all invoices the user has access to."""
    try:
        # Base query to get invoices from workspaces the user has access to
        query = (
            select(Invoice)
            .where(
                or_(
                    Invoice.workspace_id.in_(
                        select(Workspace.id)
                        .where(Workspace.owner_id == current_user.id)
                    ),
                    Invoice.workspace_id.in_(
                        select(WorkspaceMember.workspace_id)
                        .where(WorkspaceMember.user_id == current_user.id)
                    )
                )
            )
        )
        
        # Add filters if provided
        if workspace_id:
            query = query.where(Invoice.workspace_id == workspace_id)
        
        if client_id:
            query = query.where(Invoice.client_id == client_id)
        
        if status:
            query = query.where(Invoice.status == status)
        
        # Execute query
        invoices = (await session.exec(query)).all()
        return invoices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{invoice_id}", response_model=InvoiceRead, status_code=200)
async def read_invoice(
    *,
    session: DbSession,
    invoice_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific invoice."""
    try:
        # Check if user has access to the invoice's workspace
        invoice = (
            await session.exec(
                select(Invoice)
                .where(
                    Invoice.id == invoice_id,
                    or_(
                        Invoice.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Invoice.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found or access denied",
            )
        
        return invoice
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{invoice_id}", response_model=InvoiceRead, status_code=200)
async def update_invoice(
    *,
    session: DbSession,
    invoice_id: UUID,
    invoice: InvoiceUpdate,
    current_user: CurrentActiveUser,
):
    """Update an invoice."""
    try:
        # Check if user has access to update the invoice
        db_invoice = (
            await session.exec(
                select(Invoice)
                .where(
                    Invoice.id == invoice_id,
                    or_(
                        Invoice.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Invoice.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role.in_(["owner", "editor"])
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not db_invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found or you don't have permission to update it",
            )
        
        # Update invoice fields
        invoice_data = invoice.model_dump(exclude_unset=True)
        for key, value in invoice_data.items():
            setattr(db_invoice, key, value)
        
        # Update the updated_at timestamp
        from datetime import datetime, timezone
        db_invoice.updated_at = datetime.now(timezone.utc)
        
        await session.commit()
        await session.refresh(db_invoice)
        return db_invoice
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    *,
    session: DbSession,
    invoice_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete an invoice."""
    try:
        # Check if user has access to delete the invoice
        db_invoice = (
            await session.exec(
                select(Invoice)
                .where(
                    Invoice.id == invoice_id,
                    or_(
                        Invoice.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Invoice.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role == "owner"
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not db_invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found or you don't have permission to delete it",
            )
        
        await session.delete(db_invoice)
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
