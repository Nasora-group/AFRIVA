-- AFRIVA Phase 3 defense-in-depth RLS.
-- This migration is intentionally fail-closed: application code must set
-- LOCAL app.current_organization_id inside a transaction before tenant queries.

ALTER TABLE role ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS role_tenant_isolation ON role;
CREATE POLICY role_tenant_isolation ON role
    USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER)
    WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER);

DROP POLICY IF EXISTS organization_user_tenant_isolation ON organization_user;
CREATE POLICY organization_user_tenant_isolation ON organization_user
    USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER)
    WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER);

DROP POLICY IF EXISTS activity_log_tenant_isolation ON activity_log;
CREATE POLICY activity_log_tenant_isolation ON activity_log
    USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER)
    WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER);

-- PostgreSQL superusers/table owners can bypass RLS. The application role must
-- therefore NOT be a superuser and should use FORCE ROW LEVEL SECURITY where
-- operationally appropriate.
ALTER TABLE role FORCE ROW LEVEL SECURITY;
ALTER TABLE organization_user FORCE ROW LEVEL SECURITY;
ALTER TABLE activity_log FORCE ROW LEVEL SECURITY;
