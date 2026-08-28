-- AFRIVA Phase 4 CRM migration for PostgreSQL.
-- Apply through the project's migration runner; review before production.

CREATE TABLE IF NOT EXISTS commercial (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50), email VARCHAR(255), address TEXT,
    latitude NUMERIC(10,7), longitude NUMERIC(10,7),
    commercial_id INTEGER REFERENCES commercial(id) ON DELETE SET NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prospect (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50), email VARCHAR(255), address TEXT,
    latitude NUMERIC(10,7), longitude NUMERIC(10,7),
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    commercial_id INTEGER REFERENCES commercial(id) ON DELETE SET NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contact (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50), email VARCHAR(255),
    client_id INTEGER REFERENCES client(id) ON DELETE CASCADE,
    prospect_id INTEGER REFERENCES prospect(id) ON DELETE CASCADE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS visit (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), notes TEXT,
    latitude NUMERIC(10,7), longitude NUMERIC(10,7),
    commercial_id INTEGER NOT NULL REFERENCES commercial(id) ON DELETE RESTRICT,
    client_id INTEGER REFERENCES client(id) ON DELETE SET NULL,
    prospect_id INTEGER REFERENCES prospect(id) ON DELETE SET NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prospection (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    outcome VARCHAR(100) NOT NULL DEFAULT 'pending', notes TEXT,
    commercial_id INTEGER NOT NULL REFERENCES commercial(id) ON DELETE RESTRICT,
    prospect_id INTEGER REFERENCES prospect(id) ON DELETE SET NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tour (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL, tour_date DATE NOT NULL DEFAULT CURRENT_DATE,
    commercial_id INTEGER NOT NULL REFERENCES commercial(id) ON DELETE RESTRICT,
    status VARCHAR(50) NOT NULL DEFAULT 'planned',
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tour_stop (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    sequence INTEGER NOT NULL, status VARCHAR(50) NOT NULL DEFAULT 'planned',
    planned_at TIMESTAMPTZ, latitude NUMERIC(10,7), longitude NUMERIC(10,7),
    tour_id INTEGER NOT NULL REFERENCES tour(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES client(id) ON DELETE SET NULL,
    prospect_id INTEGER REFERENCES prospect(id) ON DELETE SET NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_commercial_org ON commercial(organization_id);
CREATE INDEX IF NOT EXISTS ix_client_org ON client(organization_id);
CREATE INDEX IF NOT EXISTS ix_prospect_org ON prospect(organization_id);
CREATE INDEX IF NOT EXISTS ix_contact_org ON contact(organization_id);
CREATE INDEX IF NOT EXISTS ix_visit_org ON visit(organization_id);
CREATE INDEX IF NOT EXISTS ix_prospection_org ON prospection(organization_id);
CREATE INDEX IF NOT EXISTS ix_tour_org ON tour(organization_id);
CREATE INDEX IF NOT EXISTS ix_tour_stop_org ON tour_stop(organization_id);
