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
    from .api.crm import crm_api
    from .api.inventory import inventory_api
    from .api.pos import pos_api
    from .api.sales import sales_api
    from .api.sales_dashboard import sales_dashboard_api

    app.register_blueprint(crm_api)
    app.register_blueprint(inventory_api)
    app.register_blueprint(pos_api)
    app.register_blueprint(sales_api)
    app.register_blueprint(sales_dashboard_api)

    @app.before_request
    def security_context():
        load_current_user()
        load_tenant_context()

    return app
