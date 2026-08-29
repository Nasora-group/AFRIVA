"""Import all models so SQLAlchemy metadata is complete."""

from .activity_log import ActivityLog
from .base import BaseModel, TenantAwareModel, db
from .billing import BillingPayment, Invoice, Plan, Subscription
from .crm import Client, Commercial, Note, Prospect, Prospection, Task, Tour, TourStop, Visit
from .organization import Organization
from .pos import CashSession, POSPayment, POSRegister, POSSale, POSSaleLine, Store
from .role import Permission, Role, role_permission
from .sales import Product, Sale, SaleLine, SalesTarget
from .user import OrganizationUser, User

__all__ = [
    "db", "BaseModel", "TenantAwareModel", "Organization", "User", "OrganizationUser",
    "Role", "Permission", "role_permission", "ActivityLog", "Plan", "Subscription",
    "Invoice", "BillingPayment", "Commercial", "Client", "Prospect", "Visit",
    "Prospection", "Tour", "TourStop", "Task", "Note", "Product", "Sale", "SaleLine",
    "SalesTarget", "Store", "POSRegister", "CashSession", "POSSale", "POSSaleLine", "POSPayment",
]
