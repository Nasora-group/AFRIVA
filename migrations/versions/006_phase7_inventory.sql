-- AFRIVA Phase 7 inventory foundation. Test/staging only until migration is validated.

ALTER TABLE product ADD COLUMN IF NOT EXISTS barcode VARCHAR(100);
ALTER TABLE product ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES product_category(id) ON DELETE SET NULL;
ALTER TABLE product ADD COLUMN IF NOT EXISTS purchase_price NUMERIC(12,2) NOT NULL DEFAULT 0.00;
ALTER TABLE product ADD COLUMN IF NOT EXISTS tax_rate NUMERIC(5,2) NOT NULL DEFAULT 0.00;

CREATE TABLE IF NOT EXISTS product_category (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, code)
);

CREATE TABLE IF NOT EXISTS product_stock (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    store_id INTEGER NOT NULL REFERENCES store(id) ON DELETE RESTRICT,
    quantity NUMERIC(14,3) NOT NULL DEFAULT 0,
    reserved_quantity NUMERIC(14,3) NOT NULL DEFAULT 0,
    reorder_level NUMERIC(14,3) NOT NULL DEFAULT 0,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, product_id, store_id),
    CHECK (quantity >= 0),
    CHECK (reserved_quantity >= 0),
    CHECK (reorder_level >= 0)
);

CREATE TABLE IF NOT EXISTS stock_movement (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    store_id INTEGER NOT NULL REFERENCES store(id) ON DELETE RESTRICT,
    movement_type VARCHAR(30) NOT NULL,
    quantity NUMERIC(14,3) NOT NULL,
    reference_type VARCHAR(50),
    reference_id INTEGER,
    note TEXT,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (quantity <> 0),
    CHECK (movement_type IN ('purchase','sale','return','adjustment','transfer_in','transfer_out'))
);

CREATE TABLE IF NOT EXISTS product_batch (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    store_id INTEGER NOT NULL REFERENCES store(id) ON DELETE RESTRICT,
    batch_number VARCHAR(100) NOT NULL,
    expiry_date DATE,
    quantity NUMERIC(14,3) NOT NULL DEFAULT 0,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, product_id, store_id, batch_number),
    CHECK (quantity >= 0)
);

CREATE INDEX IF NOT EXISTS ix_product_barcode ON product(barcode);
CREATE INDEX IF NOT EXISTS ix_product_category ON product(category_id);
CREATE INDEX IF NOT EXISTS ix_stock_product_store ON product_stock(product_id, store_id);
CREATE INDEX IF NOT EXISTS ix_stock_movement_product_store ON stock_movement(product_id, store_id);
CREATE INDEX IF NOT EXISTS ix_batch_expiry ON product_batch(expiry_date);
