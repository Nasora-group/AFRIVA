-- AFRIVA Phase 3 reference migration for PostgreSQL.
-- Apply through the project's migration runner; do not execute against production
-- without a backup and migration review.

CREATE TABLE IF NOT EXISTS organization (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    logo VARCHAR(500), email VARCHAR(255), phone VARCHAR(50), address TEXT,
    city VARCHAR(100), country VARCHAR(100) DEFAULT 'Senegal',
    currency VARCHAR(3) NOT NULL DEFAULT 'XOF',
    timezone VARCHAR(50) NOT NULL DEFAULT 'Africa/Dakar',
    industry VARCHAR(100), status VARCHAR(50) NOT NULL DEFAULT 'trial',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100), last_name VARCHAR(100), status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS permission (
    id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL UNIQUE, description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    name VARCHAR(100) NOT NULL, description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS organization_user (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE RESTRICT,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    role_id INTEGER NOT NULL REFERENCES role(id) ON DELETE RESTRICT,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_organization UNIQUE(user_id, organization_id)
);

CREATE TABLE IF NOT EXISTS role_permission (
    role_id INTEGER NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permission(id) ON DELETE RESTRICT,
    PRIMARY KEY(role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    user_id INTEGER REFERENCES "user"(id) ON DELETE RESTRICT,
    action VARCHAR(100) NOT NULL, resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER, ip_address VARCHAR(45), user_agent TEXT, metadata_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_role_organization_id ON role(organization_id);
CREATE INDEX IF NOT EXISTS ix_organization_user_org ON organization_user(organization_id);
CREATE INDEX IF NOT EXISTS ix_organization_user_user ON organization_user(user_id);
CREATE INDEX IF NOT EXISTS ix_activity_log_org ON activity_log(organization_id);
