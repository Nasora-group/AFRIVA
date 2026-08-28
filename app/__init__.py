"""AFRIVA Flask application factory."""
from flask import Flask

from .config import Config
from .models import db


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)

    from .auth import load_current_user
    from .middleware.tenant_middleware import load_tenant_context

    @app.before_request
    def security_context():
        load_current_user()
        load_tenant_context()

    return app
