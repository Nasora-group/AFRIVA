"""AFRIVA Flask application factory."""
from flask import Flask, g

from .config import Config
from .models import db


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)

    from .middleware.tenant_middleware import load_tenant_context

    @app.before_request
    def tenant_context():
        load_tenant_context()

    return app
