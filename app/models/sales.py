"""Sales-domain models for AFRIVA Phase 5."""

from .base import TenantAwareModel, db, utcnow


class Product(TenantAwareModel):
    __tablename__ = "product"

    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), nullable=True, index=True)
    category = db.Column(db.String(100))
    unit = db.Column(db.String(50), nullable=False, default="unit")
    unit_price = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    description = db.Column(db.Text)


class Sale(TenantAwareModel):
    __tablename__ = "sale"

    commercial_id = db.Column(
        db.Integer, db.ForeignKey("commercial.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    client_id = db.Column(
        db.Integer, db.ForeignKey("client.id", ondelete="RESTRICT"),
        nullable=True, index=True,
    )
    sold_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    status = db.Column(db.String(30), nullable=False, default="draft", index=True)
    notes = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(14, 2), nullable=False, default=0)

    commercial = db.relationship("Commercial")
    client = db.relationship("Client")
    lines = db.relationship(
        "SaleLine", back_populates="sale", cascade="all, delete-orphan"
    )

    def recalculate_total(self):
        self.total_amount = sum((line.line_total for line in self.lines), 0)


class SaleLine(TenantAwareModel):
    __tablename__ = "sale_line"

    sale_id = db.Column(
        db.Integer, db.ForeignKey("sale.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    quantity = db.Column(db.Numeric(14, 3), nullable=False, default=1)
    unit_price = db.Column(db.Numeric(14, 2), nullable=False)
    line_total = db.Column(db.Numeric(14, 2), nullable=False, default=0)

    sale = db.relationship("Sale", back_populates="lines")
    product = db.relationship("Product")

    def calculate_total(self):
        self.line_total = self.quantity * self.unit_price
        return self.line_total


class SalesTarget(TenantAwareModel):
    __tablename__ = "sales_target"

    commercial_id = db.Column(
        db.Integer, db.ForeignKey("commercial.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    year = db.Column(db.Integer, nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False, index=True)
    target_amount = db.Column(db.Numeric(14, 2), nullable=False, default=0)

    commercial = db.relationship("Commercial")

    __table_args__ = (
        db.UniqueConstraint(
            "organization_id", "commercial_id", "year", "month",
            name="uq_sales_target_org_commercial_period"
        ),
        db.CheckConstraint("month BETWEEN 1 AND 12", name="ck_sales_target_month"),
    )
