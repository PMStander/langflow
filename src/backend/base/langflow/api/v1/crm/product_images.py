from uuid import UUID
import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
import aiofiles
import uuid

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product import (
    Product,
)
from langflow.api.v1.crm.utils import (
    get_entity_access_filter,
)
from langflow.api.v1.crm.error_handling import handle_exceptions

router = APIRouter(prefix="/product-images", tags=["Product Images"])

# Define the upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../../uploads/product_images")

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/{product_id}", status_code=201)
@handle_exceptions
async def upload_product_image(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    product_id: UUID,
    image: UploadFile = File(...),
    is_primary: bool = Form(False),
):
    """Upload a product image."""
    # Check if product exists and user has access to it
    product = (
        await session.exec(
            select(Product)
            .where(
                Product.id == product_id,
                get_entity_access_filter(Product, current_user.id)
            )
        )
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or access denied",
        )
    
    # Generate a unique filename
    file_extension = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save the uploaded file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await image.read()
        await out_file.write(content)
    
    # Create image URL
    image_url = f"/uploads/product_images/{unique_filename}"
    
    # Update product images
    if product.images is None:
        product.images = []
    
    # Create image object
    image_obj = {
        "id": str(uuid.uuid4()),
        "src": image_url,
        "name": image.filename,
        "alt": image.filename,
    }
    
    # If primary image, put it first in the list
    if is_primary and product.images:
        product.images.insert(0, image_obj)
    else:
        product.images.append(image_obj)
    
    # Update product
    await session.commit()
    await session.refresh(product)
    
    return {
        "success": True,
        "image": image_obj,
        "product_id": str(product_id),
    }


@router.delete("/{product_id}/{image_id}", status_code=200)
@handle_exceptions
async def delete_product_image(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    product_id: UUID,
    image_id: str,
):
    """Delete a product image."""
    # Check if product exists and user has access to it
    product = (
        await session.exec(
            select(Product)
            .where(
                Product.id == product_id,
                get_entity_access_filter(Product, current_user.id)
            )
        )
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or access denied",
        )
    
    # Find the image in the product's images
    if not product.images:
        raise HTTPException(
            status_code=404,
            detail="Product has no images",
        )
    
    image_to_delete = None
    for i, image in enumerate(product.images):
        if image.get("id") == image_id:
            image_to_delete = product.images.pop(i)
            break
    
    if not image_to_delete:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )
    
    # Delete the image file
    image_path = os.path.join(UPLOAD_DIR, os.path.basename(image_to_delete.get("src", "")))
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # Update product
    await session.commit()
    await session.refresh(product)
    
    return {
        "success": True,
        "product_id": str(product_id),
    }


@router.put("/{product_id}/reorder", status_code=200)
@handle_exceptions
async def reorder_product_images(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    product_id: UUID,
    image_ids: List[str],
):
    """Reorder product images."""
    # Check if product exists and user has access to it
    product = (
        await session.exec(
            select(Product)
            .where(
                Product.id == product_id,
                get_entity_access_filter(Product, current_user.id)
            )
        )
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or access denied",
        )
    
    # Check if product has images
    if not product.images:
        raise HTTPException(
            status_code=404,
            detail="Product has no images",
        )
    
    # Check if all image IDs are valid
    current_image_ids = [image.get("id") for image in product.images]
    if not all(image_id in current_image_ids for image_id in image_ids):
        raise HTTPException(
            status_code=400,
            detail="Invalid image IDs",
        )
    
    # Reorder images
    reordered_images = []
    for image_id in image_ids:
        for image in product.images:
            if image.get("id") == image_id:
                reordered_images.append(image)
                break
    
    # Add any images that weren't in the reorder list
    for image in product.images:
        if image.get("id") not in image_ids:
            reordered_images.append(image)
    
    # Update product
    product.images = reordered_images
    await session.commit()
    await session.refresh(product)
    
    return {
        "success": True,
        "product_id": str(product_id),
        "images": product.images,
    }
