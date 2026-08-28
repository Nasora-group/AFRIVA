-- AFRIVA Phase 6 POS foundation migration for PostgreSQL.
-- Apply through the project's migration runner; review before production.

CREATE TABLE IF NOT EXISTS store (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL,
    address TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, code)
);

CREATE TABLE IF NOT EXISTS cash_register (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    store_id INTEGER NOT NULL REFERENCES store(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, code)
);

CREATE TABLE IF NOT EXISTS cash_session (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    register_id INTEGER NOT NULL REFERENCES cash_register(id) ON DELETE RESTRICT,
    opened_by INTEGER NOT NULL REFERENCES "user"(id) ON DELETE RESTRICT,
    closed_by INTEGER REFERENCES "user"(id) ON DELETE RESTRICT,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    opening_amount NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    closing_amount NUMERIC(12,2),
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT cash_session_status_check CHECK (status IN ('open', 'closed'))
);

CREATE INDEX IF NOT EXISTS ix_store_org ON store(organization_id);
CREATE INDEX IF NOT EXISTS ix_cash_register_org ON cash_register(organization_id);
CREATE INDEX IF NOT EXISTS ix_cash_register_store ON cash_register(store_id);
CREATE INDEX IF NOT EXISTS ix_cash_session_org ON cash_session(organization_id);
CREATE INDEX IF NOT EXISTS ix_cash_session_register ON cash_session(register_id);
CREATE INDEX IF NOT EXISTS ix_cash_session_status ON cash_session(status);
