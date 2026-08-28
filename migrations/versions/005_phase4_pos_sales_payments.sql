-- AFRIVA Phase 4 POS checkout migration for PostgreSQL.
-- Adds products, POS sales, sale lines and payments.
-- Review and apply with the project's migration runner before production.

CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100),
    unit_price NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT product_unit_price_check CHECK (unit_price >= 0),
    UNIQUE (organization_id, sku)
);

CREATE TABLE IF NOT EXISTS sale (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    sale_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'confirmed',
    commercial_id INTEGER REFERENCES commercial(id) ON DELETE SET NULL,
    client_id INTEGER REFERENCES client(id) ON DELETE SET NULL,
    cash_session_id INTEGER REFERENCES cash_session(id) ON DELETE RESTRICT,
    total_amount NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT sale_total_amount_check CHECK (total_amount >= 0)
);

CREATE TABLE IF NOT EXISTS sale_item (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    sale_id INTEGER NOT NULL REFERENCES sale(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    quantity NUMERIC(12,2) NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    line_total NUMERIC(12,2) NOT NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT sale_item_quantity_check CHECK (quantity > 0),
    CONSTRAINT sale_item_unit_price_check CHECK (unit_price >= 0),
    CONSTRAINT sale_item_line_total_check CHECK (line_total >= 0)
);

CREATE TABLE IF NOT EXISTS payment (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    sale_id INTEGER NOT NULL REFERENCES sale(id) ON DELETE CASCADE,
    cash_session_id INTEGER REFERENCES cash_session(id) ON DELETE RESTRICT,
    method VARCHAR(30) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    reference VARCHAR(255),
    status VARCHAR(30) NOT NULL DEFAULT 'confirmed',
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT payment_amount_check CHECK (amount > 0),
    CONSTRAINT payment_method_check CHECK (
        method IN ('cash', 'card', 'mobile_money', 'bank_transfer', 'check')
    )
);

CREATE TABLE IF NOT EXISTS sales_target (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    target_amount NUMERIC(12,2) NOT NULL,
    commercial_id INTEGER REFERENCES commercial(id) ON DELETE SET NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT sales_target_month_check CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT sales_target_amount_check CHECK (target_amount >= 0)
);

CREATE INDEX IF NOT EXISTS ix_product_org ON product(organization_id);
CREATE INDEX IF NOT EXISTS ix_product_sku ON product(sku);
CREATE INDEX IF NOT EXISTS ix_sale_org ON sale(organization_id);
CREATE INDEX IF NOT EXISTS ix_sale_date ON sale(sale_date);
CREATE INDEX IF NOT EXISTS ix_sale_cash_session ON sale(cash_session_id);
CREATE INDEX IF NOT EXISTS ix_sale_item_org ON sale_item(organization_id);
CREATE INDEX IF NOT EXISTS ix_sale_item_sale ON sale_item(sale_id);
CREATE INDEX IF NOT EXISTS ix_sale_item_product ON sale_item(product_id);
CREATE INDEX IF NOT EXISTS ix_payment_org ON payment(organization_id);
CREATE INDEX IF NOT EXISTS ix_payment_sale ON payment(sale_id);
CREATE INDEX IF NOT EXISTS ix_payment_cash_session ON payment(cash_session_id);
CREATE INDEX IF NOT EXISTS ix_sales_target_org ON sales_target(organization_id);
