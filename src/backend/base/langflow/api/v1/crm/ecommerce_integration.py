from uuid import UUID
import json
from typing import Dict, List, Optional, Any
import httpx
from fastapi import APIRouter, HTTPException, status, Query, Body

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product import (
    Product,
    ProductCreate,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
)
from langflow.api.v1.crm.error_handling import handle_exceptions

router = APIRouter(prefix="/ecommerce-integration", tags=["E-commerce Integration"])


@router.post("/import-woocommerce", status_code=201)
@handle_exceptions
async def import_woocommerce_products(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID,
    site_url: str = Body(...),
    consumer_key: str = Body(...),
    consumer_secret: str = Body(...),
    limit: int = Body(10),
):
    """Import products from WooCommerce."""
    # Check if user has access to the workspace
    await check_workspace_access(session, workspace_id, current_user)
    
    # Build WooCommerce API URL
    api_url = f"{site_url.rstrip('/')}/wp-json/wc/v3/products"
    
    # Set up parameters
    params = {
        "per_page": limit,
        "status": "publish",
    }
    
    try:
        # Make API request to WooCommerce
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url,
                params=params,
                auth=(consumer_key, consumer_secret),
                timeout=30.0,
            )
            
            # Check if request was successful
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"WooCommerce API request failed: {response.text}",
                )
            
            # Parse response
            woo_products = response.json()
            
            # Import products
            imported_products = []
            errors = []
            
            for woo_product in woo_products:
                try:
                    # Map WooCommerce product to our product model
                    product_data = {
                        "name": woo_product.get("name", ""),
                        "slug": woo_product.get("slug", ""),
                        "description": woo_product.get("description", ""),
                        "short_description": woo_product.get("short_description", ""),
                        "sku": woo_product.get("sku", ""),
                        "price": float(woo_product.get("price", 0)),
                        "regular_price": float(woo_product.get("regular_price", 0)) if woo_product.get("regular_price") else 0,
                        "sale_price": float(woo_product.get("sale_price", 0)) if woo_product.get("sale_price") else None,
                        "on_sale": woo_product.get("on_sale", False),
                        "status": woo_product.get("status", "publish"),
                        "featured": woo_product.get("featured", False),
                        "catalog_visibility": woo_product.get("catalog_visibility", "visible"),
                        "tax_status": woo_product.get("tax_status", "taxable"),
                        "tax_class": woo_product.get("tax_class", ""),
                        "manage_stock": woo_product.get("manage_stock", False),
                        "stock_quantity": woo_product.get("stock_quantity", None),
                        "stock_status": woo_product.get("stock_status", "instock"),
                        "backorders": woo_product.get("backorders", "no"),
                        "backorders_allowed": woo_product.get("backorders_allowed", False),
                        "backordered": woo_product.get("backordered", False),
                        "weight": woo_product.get("weight", ""),
                        "dimensions": woo_product.get("dimensions", {}),
                        "shipping_class": woo_product.get("shipping_class", ""),
                        "shipping_class_id": woo_product.get("shipping_class_id", None),
                        "virtual": woo_product.get("virtual", False),
                        "downloadable": woo_product.get("downloadable", False),
                        "downloads": woo_product.get("downloads", []),
                        "download_limit": woo_product.get("download_limit", -1),
                        "download_expiry": woo_product.get("download_expiry", -1),
                        "sold_individually": woo_product.get("sold_individually", False),
                        "external_url": woo_product.get("external_url", ""),
                        "button_text": woo_product.get("button_text", ""),
                        "menu_order": woo_product.get("menu_order", 0),
                        "purchasable": woo_product.get("purchasable", True),
                        "images": woo_product.get("images", []),
                        "workspace_id": str(workspace_id),
                    }
                    
                    # Create product
                    product_create = ProductCreate(**product_data)
                    db_product = Product.model_validate(product_create)
                    db_product.created_by = current_user.id
                    
                    # Add to session
                    session.add(db_product)
                    await session.commit()
                    await session.refresh(db_product)
                    
                    imported_products.append(db_product)
                except Exception as e:
                    # Rollback session
                    await session.rollback()
                    
                    # Add error to list
                    errors.append({
                        "product": woo_product.get("name", "Unknown"),
                        "error": str(e)
                    })
            
            # Return results
            return {
                "success": len(imported_products),
                "errors": len(errors),
                "error_details": errors,
                "products": [p.model_dump() for p in imported_products]
            }
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to WooCommerce: {str(e)}",
        )


@router.post("/import-shopify", status_code=201)
@handle_exceptions
async def import_shopify_products(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID,
    shop_url: str = Body(...),
    access_token: str = Body(...),
    limit: int = Body(10),
):
    """Import products from Shopify."""
    # Check if user has access to the workspace
    await check_workspace_access(session, workspace_id, current_user)
    
    # Build Shopify API URL
    api_url = f"https://{shop_url.replace('https://', '').replace('http://', '').rstrip('/')}/admin/api/2023-04/products.json"
    
    # Set up headers
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }
    
    # Set up parameters
    params = {
        "limit": limit,
    }
    
    try:
        # Make API request to Shopify
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url,
                params=params,
                headers=headers,
                timeout=30.0,
            )
            
            # Check if request was successful
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Shopify API request failed: {response.text}",
                )
            
            # Parse response
            shopify_data = response.json()
            shopify_products = shopify_data.get("products", [])
            
            # Import products
            imported_products = []
            errors = []
            
            for shopify_product in shopify_products:
                try:
                    # Get first variant for pricing info
                    variant = shopify_product.get("variants", [{}])[0]
                    
                    # Map Shopify product to our product model
                    product_data = {
                        "name": shopify_product.get("title", ""),
                        "slug": shopify_product.get("handle", ""),
                        "description": shopify_product.get("body_html", ""),
                        "short_description": "",
                        "sku": variant.get("sku", ""),
                        "price": float(variant.get("price", 0)),
                        "regular_price": float(variant.get("compare_at_price", 0)) if variant.get("compare_at_price") else float(variant.get("price", 0)),
                        "sale_price": float(variant.get("price", 0)) if variant.get("compare_at_price") else None,
                        "on_sale": bool(variant.get("compare_at_price")),
                        "status": "publish" if shopify_product.get("status") == "active" else "draft",
                        "featured": shopify_product.get("published", False),
                        "catalog_visibility": "visible",
                        "tax_status": "taxable",
                        "tax_class": "",
                        "manage_stock": variant.get("inventory_management") == "shopify",
                        "stock_quantity": variant.get("inventory_quantity", None),
                        "stock_status": "instock" if variant.get("inventory_quantity", 0) > 0 else "outofstock",
                        "backorders": "no",
                        "backorders_allowed": False,
                        "backordered": False,
                        "weight": str(variant.get("weight", "")),
                        "dimensions": {
                            "length": "",
                            "width": "",
                            "height": "",
                        },
                        "shipping_class": "",
                        "shipping_class_id": None,
                        "virtual": False,
                        "downloadable": False,
                        "downloads": [],
                        "download_limit": -1,
                        "download_expiry": -1,
                        "sold_individually": False,
                        "external_url": "",
                        "button_text": "",
                        "menu_order": 0,
                        "purchasable": True,
                        "images": [
                            {
                                "id": str(img.get("id", "")),
                                "src": img.get("src", ""),
                                "name": img.get("alt", ""),
                                "alt": img.get("alt", ""),
                            }
                            for img in shopify_product.get("images", [])
                        ],
                        "workspace_id": str(workspace_id),
                    }
                    
                    # Create product
                    product_create = ProductCreate(**product_data)
                    db_product = Product.model_validate(product_create)
                    db_product.created_by = current_user.id
                    
                    # Add to session
                    session.add(db_product)
                    await session.commit()
                    await session.refresh(db_product)
                    
                    imported_products.append(db_product)
                except Exception as e:
                    # Rollback session
                    await session.rollback()
                    
                    # Add error to list
                    errors.append({
                        "product": shopify_product.get("title", "Unknown"),
                        "error": str(e)
                    })
            
            # Return results
            return {
                "success": len(imported_products),
                "errors": len(errors),
                "error_details": errors,
                "products": [p.model_dump() for p in imported_products]
            }
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to Shopify: {str(e)}",
        )
