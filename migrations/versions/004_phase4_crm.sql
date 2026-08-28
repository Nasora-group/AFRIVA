-- Phase 4 CRM: tenant-aware CRM entities and PostgreSQL RLS.
-- Apply after 001_phase3_foundation.sql and 002_phase3_rls.sql.

CREATE TABLE IF NOT EXISTS commercial (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS ix_commercial_org ON commercial(organization_id);

CREATE TABLE IF NOT EXISTS client (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    name VARCHAR(255) NOT NULL,
    client_type VARCHAR(50) NOT NULL DEFAULT 'business',
    sector VARCHAR(100), email VARCHAR(255), phone VARCHAR(50),
    address TEXT, city VARCHAR(100), latitude NUMERIC(10,7), longitude NUMERIC(10,7),
    status VARCHAR(30) NOT NULL DEFAULT 'active', notes TEXT
);
CREATE INDEX IF NOT EXISTS ix_client_org ON client(organization_id);
CREATE INDEX IF NOT EXISTS ix_client_status ON client(status);

CREATE TABLE IF NOT EXISTS prospect (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255), phone VARCHAR(50), email VARCHAR(255),
    address TEXT, city VARCHAR(100), latitude NUMERIC(10,7), longitude NUMERIC(10,7),
    status VARCHAR(30) NOT NULL DEFAULT 'new', potential NUMERIC(14,2), notes TEXT
);
CREATE INDEX IF NOT EXISTS ix_prospect_org ON prospect(organization_id);
CREATE INDEX IF NOT EXISTS ix_prospect_status ON prospect(status);

CREATE TABLE IF NOT EXISTS visit (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ,
    commercial_id INTEGER NOT NULL REFERENCES commercial(id) ON DELETE RESTRICT,
    client_id INTEGER REFERENCES client(id) ON DELETE RESTRICT,
    prospect_id INTEGER REFERENCES prospect(id) ON DELETE RESTRICT,
    visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), duration_minutes INTEGER,
    latitude NUMERIC(10,7), longitude NUMERIC(10,7), objective TEXT, result TEXT, notes TEXT,
    CONSTRAINT ck_visit_target CHECK ((client_id IS NOT NULL) OR (prospect_id IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS ix_visit_org ON visit(organization_id);
CREATE INDEX IF NOT EXISTS ix_visit_commercial ON visit(commercial_id);

CREATE TABLE IF NOT EXISTS prospection (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ,
    commercial_id INTEGER NOT NULL REFERENCES commercial(id) ON DELETE RESTRICT,
    prospect_id INTEGER NOT NULL REFERENCES prospect(id) ON DELETE RESTRICT,
    reason TEXT, interlocutor VARCHAR(255), potential NUMERIC(14,2), next_action TEXT,
    follow_up_at TIMESTAMPTZ, status VARCHAR(30) NOT NULL DEFAULT 'open', notes TEXT
);
CREATE INDEX IF NOT EXISTS ix_prospection_org ON prospection(organization_id);
CREATE INDEX IF NOT EXISTS ix_prospection_commercial ON prospection(commercial_id);

CREATE TABLE IF NOT EXISTS tour (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ,
    commercial_id INTEGER NOT NULL REFERENCES commercial(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL, planned_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'planned', started_at TIMESTAMPTZ, completed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_tour_org ON tour(organization_id);
CREATE INDEX IF NOT EXISTS ix_tour_date ON tour(planned_date);

CREATE TABLE IF NOT EXISTS tour_stop (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ,
    tour_id INTEGER NOT NULL REFERENCES tour(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES client(id) ON DELETE RESTRICT,
    prospect_id INTEGER REFERENCES prospect(id) ON DELETE RESTRICT,
    position INTEGER NOT NULL DEFAULT 1, status VARCHAR(30) NOT NULL DEFAULT 'planned',
    visited_at TIMESTAMPTZ, notes TEXT
);
CREATE INDEX IF NOT EXISTS ix_tour_stop_org ON tour_stop(organization_id);

CREATE TABLE IF NOT EXISTS crm_task (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ,
    commercial_id INTEGER REFERENCES commercial(id) ON DELETE RESTRICT,
    client_id INTEGER REFERENCES client(id) ON DELETE RESTRICT,
    prospect_id INTEGER REFERENCES prospect(id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL, description TEXT, due_at TIMESTAMPTZ,
    status VARCHAR(30) NOT NULL DEFAULT 'open'
);
CREATE INDEX IF NOT EXISTS ix_crm_task_org ON crm_task(organization_id);

CREATE TABLE IF NOT EXISTS crm_note (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ,
    commercial_id INTEGER REFERENCES commercial(id) ON DELETE RESTRICT,
    client_id INTEGER REFERENCES client(id) ON DELETE RESTRICT,
    prospect_id INTEGER REFERENCES prospect(id) ON DELETE RESTRICT,
    body TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_crm_note_org ON crm_note(organization_id);

-- Defense in depth: every CRM table is isolated by the server-side tenant setting.
DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['commercial','client','prospect','visit','prospection','tour','tour_stop','crm_task','crm_note'] LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS %I_tenant_isolation ON %I', t, t);
    EXECUTE format(
      'CREATE POLICY %I_tenant_isolation ON %I USING (organization_id = NULLIF(current_setting(''app.current_organization_id'', true), '''')::INTEGER) WITH CHECK (organization_id = NULLIF(current_setting(''app.current_organization_id'', true), '''')::INTEGER)',
      t, t
    );
  END LOOP;
END $$;
