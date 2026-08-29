"""Apply AFRIVA's ordered PostgreSQL SQL migrations safely."""

from pathlib import Path

import psycopg2
from flask import current_app

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations" / "versions"


def database_url():
    url = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    if not url:
        raise RuntimeError("DATABASE_URL / SQLALCHEMY_DATABASE_URI is not configured")
    return url.replace("postgresql+psycopg2://", "postgresql://", 1)


def migrate():
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migrations:
        raise RuntimeError(f"No SQL migrations found in {MIGRATIONS_DIR}")

    with psycopg2.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute("SELECT pg_advisory_xact_lock(7420212026)")

            for migration in migrations:
                version = migration.name
                cur.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = %s",
                    (version,),
                )
                if cur.fetchone():
                    continue

                sql = migration.read_text(encoding="utf-8")
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (version,),
                )

        conn.commit()


def main():
    from app import create_app

    app = create_app()
    with app.app_context():
        migrate()
    print("AFRIVA SQL migrations applied successfully.")


if __name__ == "__main__":
    main()
