"""AFRIVA Flask application factory."""

from flask import Flask, jsonify, request

from .config import Config
from .models import db


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)

    @app.get("/health")
    def health():
        """Lightweight Render readiness endpoint."""
        return jsonify({"status": "ok"}), 200

    @app.get("/")
    def index():
        """Basic service endpoint for smoke tests and browser access."""
        return jsonify({"service": "AFRIVA", "status": "ok"}), 200

    from .auth import load_current_user
    from .middleware.tenant_middleware import load_tenant_context

    @app.before_request
    def security_context():
        # Keep the infrastructure health endpoint independent from session and
        # tenant database lookups so Render can reliably determine readiness.
        if request.path == "/health":
            return None
        load_current_user()
        load_tenant_context()
        return None

    return app
