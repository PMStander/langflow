from fastapi import APIRouter

from .clients import router as clients_router
from .invoices import router as invoices_router
from .opportunities import router as opportunities_router
from .tasks import router as tasks_router
from .dashboard import router as dashboard_router
from .reports import router as reports_router
from .products import router as products_router
from .product_categories import router as product_categories_router
from .product_attributes import router as product_attributes_router
from .product_variations import router as product_variations_router
from .product_meta import router as product_meta_router
from .product_import_export import router as product_import_export_router
from .product_images import router as product_images_router
from .product_reviews import router as product_reviews_router
from .ecommerce_integration import router as ecommerce_integration_router

__all__ = [
    "clients_router",
    "invoices_router",
    "opportunities_router",
    "tasks_router",
    "dashboard_router",
    "reports_router",
    "products_router",
    "product_categories_router",
    "product_attributes_router",
    "product_variations_router",
    "product_meta_router",
    "product_import_export_router",
    "product_images_router",
    "product_reviews_router",
    "ecommerce_integration_router",
]
