import os
import sys
import types
from dotenv import load_dotenv
import logging

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

if __package__ in (None, ""):
    package = types.ModuleType("nyiso_api")
    package.__path__ = [os.path.dirname(os.path.abspath(__file__))]
    sys.modules.setdefault("nyiso_api", package)

from nyiso_api.extensions import db
from nyiso_api.models import *
from nyiso_api.resources import __all__ as resource_definitions
from nyiso_api.utils.configure_logging import ConfigureLogging

def create_app():
    app = Flask(__name__)
    api = Api(app)

    for _, cls, route in resource_definitions:
        api.add_resource(cls, route)

    # Load .env file and set config
    load_dotenv()
    DATABASE_URL = f"postgresql+psycopg2://{os.getenv('PG_USER')}:${os.getenv('PG_PASSWORD')}@db:5432/${os.getenv('PG_DATABASE')}"
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    ConfigureLogging(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5050,debug=False)
