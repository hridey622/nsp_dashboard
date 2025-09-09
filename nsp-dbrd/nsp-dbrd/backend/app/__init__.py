from flask import Flask
from .config import Config
from .routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints or routes
    app.register_blueprint(api)

    return app