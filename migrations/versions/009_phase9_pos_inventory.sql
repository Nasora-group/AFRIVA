-- AFRIVA Phase 9: POS sales are tied to store inventory through the register.
-- No schema change is required for the existing POS sale tables; this migration
-- adds the supporting indexes used by the stock-consumption path.

CREATE INDEX IF NOT EXISTS ix_product_stock_pos_lookup
    ON product_stock(organization_id, store_id, product_id);

CREATE INDEX IF NOT EXISTS ix_product_batch_pos_fefo
    ON product_batch(organization_id, store_id, product_id, expiry_date, id);
