"""Environment-only application configuration."""

import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    )

    @classmethod
    def validate(cls):
        missing = [
            name
            for name, value in {
                "SECRET_KEY": cls.SECRET_KEY,
                "DATABASE_URL": cls.SQLALCHEMY_DATABASE_URI,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
