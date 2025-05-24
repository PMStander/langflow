# Router for base api
from fastapi import APIRouter

from langflow.api.v1 import (
    ai_assistant_router,
    api_key_router,
    books_router,
    chat_router,
    endpoints_router,
    files_router,
    flows_router,
    folders_router,
    login_router,
    mcp_projects_router,
    mcp_router,
    monitor_router,
    projects_router,
    starter_projects_router,
    store_router,
    templates_router,
    users_router,
    validate_router,
    variables_router,
    voice_mode_router,
    workspaces_router,
    workspace_members_router,
)
from langflow.api.v1.crm import (
    clients_router,
    invoices_router,
    opportunities_router,
    tasks_router,
    dashboard_router,
    reports_router,
    products_router,
    product_categories_router,
    product_attributes_router,
    product_variations_router,
    product_meta_router,
    product_import_export_router,
    product_images_router,
    product_reviews_router,
    ecommerce_integration_router,
)
from langflow.api.v2 import files_router as files_router_v2

router = APIRouter(
    prefix="/api",
)

router_v1 = APIRouter(
    prefix="/v1",
)

router_v2 = APIRouter(
    prefix="/v2",
)

router_v1.include_router(ai_assistant_router)
router_v1.include_router(chat_router)
router_v1.include_router(endpoints_router)
router_v1.include_router(validate_router)
router_v1.include_router(store_router)
router_v1.include_router(flows_router)
router_v1.include_router(users_router)
router_v1.include_router(api_key_router)
router_v1.include_router(login_router)
router_v1.include_router(variables_router)
router_v1.include_router(files_router)
router_v1.include_router(monitor_router)
router_v1.include_router(folders_router)
router_v1.include_router(projects_router)
router_v1.include_router(starter_projects_router)
router_v1.include_router(voice_mode_router)
router_v1.include_router(mcp_router)
router_v1.include_router(mcp_projects_router)
router_v1.include_router(workspaces_router)
router_v1.include_router(workspace_members_router)

# Book Creator routers
router_v1.include_router(books_router)
router_v1.include_router(templates_router)

# CRM routers
router_v1.include_router(clients_router)
router_v1.include_router(invoices_router)
router_v1.include_router(opportunities_router)
router_v1.include_router(tasks_router)
router_v1.include_router(dashboard_router)
router_v1.include_router(reports_router)
router_v1.include_router(products_router)
router_v1.include_router(product_categories_router)
router_v1.include_router(product_attributes_router)
router_v1.include_router(product_variations_router)
router_v1.include_router(product_meta_router)

router_v2.include_router(files_router_v2)

router.include_router(router_v1)
router.include_router(router_v2)
