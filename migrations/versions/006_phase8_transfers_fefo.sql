-- AFRIVA Phase 8: inter-store transfers and pharmacy batch tracking.

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
    CONSTRAINT product_batch_quantity_check CHECK (quantity >= 0)
);

CREATE TABLE IF NOT EXISTS stock_transfer (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    source_store_id INTEGER NOT NULL REFERENCES store(id) ON DELETE RESTRICT,
    destination_store_id INTEGER NOT NULL REFERENCES store(id) ON DELETE RESTRICT,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    reference VARCHAR(100),
    note TEXT,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT stock_transfer_stores_check CHECK (source_store_id <> destination_store_id)
);

CREATE TABLE IF NOT EXISTS stock_transfer_item (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    transfer_id INTEGER NOT NULL REFERENCES stock_transfer(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    quantity NUMERIC(14,3) NOT NULL,
    batch_id INTEGER REFERENCES product_batch(id) ON DELETE RESTRICT,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT stock_transfer_item_quantity_check CHECK (quantity > 0)
);

CREATE INDEX IF NOT EXISTS ix_product_batch_lookup
    ON product_batch(organization_id, product_id, store_id, expiry_date);
CREATE INDEX IF NOT EXISTS ix_stock_transfer_org_status
    ON stock_transfer(organization_id, status);
CREATE INDEX IF NOT EXISTS ix_stock_transfer_item_transfer
    ON stock_transfer_item(transfer_id);
