from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.invoice import (
    Invoice,
    InvoiceCreate,
    InvoiceRead,
    InvoiceUpdate,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse

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
        # Check if user has access to the workspace with edit permission
        await check_workspace_access(
            session,
            invoice.workspace_id,
            current_user,
            require_edit_permission=True
        )

        # Create the invoice
        db_invoice = Invoice(
            **invoice.model_dump(),
            created_by=current_user.id,
        )
        # Update timestamps
        update_entity_timestamps(db_invoice, is_new=True)
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


@router.get("/", response_model=PaginatedResponse[InvoiceRead], status_code=200)
async def read_invoices(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    client_id: UUID | None = None,
    invoice_status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    page: int | None = None,
):
    """
    Get all invoices the user has access to.

    Supports pagination with skip/limit or page/limit parameters.
    Returns a paginated response with items and metadata.
    """
    try:
        # Base query to get invoices from workspaces the user has access to
        query = (
            select(Invoice)
            .where(get_entity_access_filter(Invoice, current_user.id))
        )

        # Add filters if provided
        if workspace_id:
            query = query.where(Invoice.workspace_id == workspace_id)

        if client_id:
            query = query.where(Invoice.client_id == client_id)

        if invoice_status:
            query = query.where(Invoice.status == invoice_status)

        # Apply pagination and get items with metadata
        invoices, metadata = await paginate_query(
            session=session,
            query=query,
            skip=skip,
            limit=limit,
            page=page
        )

        # Return paginated response
        return PaginatedResponse(items=invoices, metadata=metadata)
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
        # Check if invoice exists and user has access to it
        invoice = (
            await session.exec(
                select(Invoice)
                .where(
                    Invoice.id == invoice_id,
                    get_entity_access_filter(Invoice, current_user.id)
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
        # Check if invoice exists
        db_invoice = (
            await session.exec(
                select(Invoice)
                .where(Invoice.id == invoice_id)
            )
        ).first()

        if not db_invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )

        # Check if user has edit permission for the invoice's workspace
        await check_workspace_access(
            session,
            db_invoice.workspace_id,
            current_user,
            require_edit_permission=True
        )

        # Update invoice fields and timestamps
        invoice_data = invoice.model_dump(exclude_unset=True)
        update_entity_timestamps(db_invoice, update_data=invoice_data)

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
        # Check if invoice exists
        db_invoice = (
            await session.exec(
                select(Invoice)
                .where(Invoice.id == invoice_id)
            )
        ).first()

        if not db_invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )

        # Check if user has owner permission for the invoice's workspace
        await check_workspace_access(
            session,
            db_invoice.workspace_id,
            current_user,
            require_owner_permission=True
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
