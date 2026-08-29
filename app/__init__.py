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
        """Lightweight readiness endpoint."""
        return jsonify({"status": "ok"}), 200

    @app.get("/")
    def index():
        """Basic service endpoint for smoke tests."""
        return jsonify({"service": "AFRIVA", "status": "ok"}), 200

    from .api.analytics import analytics_api
    from .api.billing import billing_api
    from .api.inventory import inventory_api
    from .api.transfers import transfers_api
    from . import auth
    from .middleware import tenant_middleware
    from .routes.pos import pos_bp
    from .routes.sales import sales_bp

    app.register_blueprint(sales_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(inventory_api)
    app.register_blueprint(transfers_api)
    app.register_blueprint(billing_api)
    app.register_blueprint(analytics_api)

    @app.before_request
    def security_context():
        if request.path in {"/", "/health"}:
            return None
        auth.load_current_user()
        tenant_middleware.load_tenant_context()
        return None

    return app
