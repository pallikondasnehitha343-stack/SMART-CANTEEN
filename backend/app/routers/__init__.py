from app.routers.auth import router as auth_router
from app.routers.menu import router as menu_router
from app.routers.pickup import router as pickup_router
from app.routers.orders import router as orders_router
from app.routers.queue import router as queue_router
from app.routers.payments import router as payments_router
from app.routers.inventory import router as inventory_router
from app.routers.kitchen import router as kitchen_router
from app.routers.admin import router as admin_router
from app.routers.analytics import router as analytics_router
from app.routers.notifications import router as notifications_router

__all__ = [
    "auth_router",
    "menu_router",
    "pickup_router",
    "orders_router",
    "queue_router",
    "payments_router",
    "inventory_router",
    "kitchen_router",
    "admin_router",
    "analytics_router",
    "notifications_router",
]
