"""Import all models so SQLAlchemy metadata is complete."""

from .activity_log import ActivityLog
from .base import BaseModel, TenantAwareModel, db
from .crm import Client, Commercial, Contact, Prospect, Prospection, Tour, TourStop, Visit
from .organization import Organization
from .pos import CashRegister, CashSession, Store
from .role import Permission, Role, role_permission
from .sales import Product, Sale, SaleItem, SalesTarget
from .user import OrganizationUser, User

__all__ = [
    "db",
    "BaseModel",
    "TenantAwareModel",
    "Organization",
    "User",
    "OrganizationUser",
    "Role",
    "Permission",
    "role_permission",
    "ActivityLog",
    "Commercial",
    "Client",
    "Prospect",
    "Contact",
    "Visit",
    "Prospection",
    "Tour",
    "TourStop",
    "Product",
    "Sale",
    "SaleItem",
    "SalesTarget",
    "Store",
    "CashRegister",
    "CashSession",
]
