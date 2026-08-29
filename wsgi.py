"""WSGI entry point for AFRIVA."""

from app import create_app
from app.routes.sales import sales_bp

app = create_app()
app.register_blueprint(sales_bp)
