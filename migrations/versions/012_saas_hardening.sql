-- AFRIVA SaaS hardening: billing tenant isolation and safe default plans.
-- Idempotent PostgreSQL migration. Apply with scripts/migrate_sql.py.

-- Billing data is tenant data and must receive the same defense-in-depth RLS
-- protection as CRM, sales, POS and inventory.
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'billing_subscription',
        'billing_invoice',
        'billing_payment'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS %I_tenant_isolation ON %I', t, t);
        EXECUTE format(
            'CREATE POLICY %I_tenant_isolation ON %I USING (organization_id = NULLIF(current_setting(''app.current_organization_id'', true), '''')::INTEGER) WITH CHECK (organization_id = NULLIF(current_setting(''app.current_organization_id'', true), '''')::INTEGER)',
            t, t
        );
    END LOOP;
END $$;

-- Plans are global catalogue data, so they intentionally remain readable by
-- authenticated tenants without an organization filter.
INSERT INTO billing_plan (
    code, name, description, monthly_price, yearly_price, trial_days,
    max_users, max_stores, max_products, active
) VALUES
    ('starter', 'Starter', 'Pour une petite structure', 9900, 99000, 14, 5, 1, 500, TRUE),
    ('business', 'Business', 'Pour les équipes commerciales et points de vente', 24900, 249000, 14, 20, 5, 2500, TRUE),
    ('enterprise', 'Enterprise', 'Pour les organisations multi-sites', 59900, 599000, 30, NULL, NULL, NULL, TRUE)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    monthly_price = EXCLUDED.monthly_price,
    yearly_price = EXCLUDED.yearly_price,
    trial_days = EXCLUDED.trial_days,
    max_users = EXCLUDED.max_users,
    max_stores = EXCLUDED.max_stores,
    max_products = EXCLUDED.max_products,
    active = EXCLUDED.active;

CREATE INDEX IF NOT EXISTS ix_billing_subscription_org_period
    ON billing_subscription(organization_id, current_period_end);
CREATE INDEX IF NOT EXISTS ix_billing_payment_org_status
    ON billing_payment(organization_id, status);
