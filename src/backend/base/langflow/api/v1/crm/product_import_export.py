from uuid import UUID
import csv
import io
import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product import (
    Product,
    ProductCreate,
    ProductRead,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
)
from langflow.api.v1.crm.error_handling import handle_exceptions

router = APIRouter(prefix="/product-import-export", tags=["Product Import/Export"])


@router.post("/import", status_code=201)
@handle_exceptions
async def import_products(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID,
    file: UploadFile = File(...),
    format: str = Query("csv", enum=["csv", "json"]),
):
    """Import products from a CSV or JSON file."""
    # Check if user has access to the workspace
    await check_workspace_access(session, workspace_id, current_user)
    
    # Read file content
    content = await file.read()
    
    # Parse file based on format
    products_data = []
    if format == "csv":
        # Parse CSV
        text_content = content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(text_content))
        for row in csv_reader:
            # Convert string values to appropriate types
            if "price" in row:
                row["price"] = float(row["price"]) if row["price"] else 0.0
            if "regular_price" in row:
                row["regular_price"] = float(row["regular_price"]) if row["regular_price"] else 0.0
            if "sale_price" in row:
                row["sale_price"] = float(row["sale_price"]) if row["sale_price"] and row["sale_price"] != "None" else None
            if "on_sale" in row:
                row["on_sale"] = row["on_sale"].lower() == "true"
            if "featured" in row:
                row["featured"] = row["featured"].lower() == "true"
            if "manage_stock" in row:
                row["manage_stock"] = row["manage_stock"].lower() == "true"
            if "stock_quantity" in row:
                row["stock_quantity"] = int(row["stock_quantity"]) if row["stock_quantity"] and row["stock_quantity"] != "None" else None
            
            # Add workspace_id
            row["workspace_id"] = str(workspace_id)
            products_data.append(row)
    else:
        # Parse JSON
        products_data = json.loads(content)
        if not isinstance(products_data, list):
            products_data = [products_data]
        
        # Add workspace_id to each product
        for product in products_data:
            product["workspace_id"] = str(workspace_id)
    
    # Create products
    created_products = []
    errors = []
    
    for idx, product_data in enumerate(products_data):
        try:
            # Create product
            product_create = ProductCreate(**product_data)
            db_product = Product.model_validate(product_create)
            db_product.created_by = current_user.id
            
            # Add to session
            session.add(db_product)
            await session.commit()
            await session.refresh(db_product)
            
            created_products.append(db_product)
        except Exception as e:
            # Rollback session
            await session.rollback()
            
            # Add error to list
            errors.append({
                "index": idx,
                "data": product_data,
                "error": str(e)
            })
    
    # Return results
    return {
        "success": len(created_products),
        "errors": len(errors),
        "error_details": errors,
        "products": created_products
    }


@router.get("/export")
@handle_exceptions
async def export_products(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: Optional[UUID] = None,
    format: str = Query("csv", enum=["csv", "json"]),
):
    """Export products to a CSV or JSON file."""
    # Build query
    query = select(Product).where(get_entity_access_filter(Product, current_user.id))
    
    # Filter by workspace if provided
    if workspace_id:
        query = query.where(Product.workspace_id == workspace_id)
    
    # Execute query
    products = (await session.exec(query)).all()
    
    # Convert products to dict
    products_data = [product.model_dump() for product in products]
    
    # Export based on format
    if format == "csv":
        # Create CSV
        output = io.StringIO()
        if products_data:
            writer = csv.DictWriter(output, fieldnames=products_data[0].keys())
            writer.writeheader()
            writer.writerows(products_data)
        
        # Return CSV response
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=products.csv"}
        )
    else:
        # Return JSON response
        return Response(
            content=json.dumps(products_data, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=products.json"}
        )
