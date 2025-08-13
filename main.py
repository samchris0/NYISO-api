import os
from dotenv import load_dotenv
import logging

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from extensions import db
from models import *
from resources import __all__ as resource_definitions
from utils.configure_logging import ConfigureLogging

def create_app():
    app = Flask(__name__)
    api = Api(app)

    for _, cls, route in resource_definitions:
        api.add_resource(cls, route)

    # Load .env file and set config
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        #db.drop_all()
        db.create_all()

    ConfigureLogging(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)