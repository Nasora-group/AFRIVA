-- Allow the application to discover a user's active tenant membership during login.
-- The user id is supplied only from the authenticated Flask session context.
DROP POLICY IF EXISTS organization_user_tenant_isolation ON organization_user;
CREATE POLICY organization_user_tenant_isolation ON organization_user
    USING (
        organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER
        OR user_id = NULLIF(current_setting('app.current_user_id', true), '')::INTEGER
    )
    WITH CHECK (
        organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER
    );
