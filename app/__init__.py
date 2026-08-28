"""AFRIVA Flask application factory."""
from flask import Flask


def create_app(config_object=None):
    app = Flask(__name__)
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_prefixed_env()
    return app
