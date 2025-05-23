from fastapi import APIRouter

from .clients import router as clients_router
from .invoices import router as invoices_router
from .opportunities import router as opportunities_router
from .tasks import router as tasks_router
from .dashboard import router as dashboard_router
from .reports import router as reports_router

__all__ = [
    "clients_router",
    "invoices_router",
    "opportunities_router",
    "tasks_router",
    "dashboard_router",
    "reports_router",
]
