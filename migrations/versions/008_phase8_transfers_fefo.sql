-- AFRIVA Phase 8: inter-store transfers and batch traceability.

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
    CHECK (source_store_id <> destination_store_id)
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
    CHECK (quantity > 0)
);

CREATE INDEX IF NOT EXISTS ix_stock_transfer_org_status
    ON stock_transfer(organization_id, status);
CREATE INDEX IF NOT EXISTS ix_stock_transfer_item_transfer
    ON stock_transfer_item(transfer_id);
CREATE INDEX IF NOT EXISTS ix_stock_transfer_item_batch
    ON stock_transfer_item(batch_id);
