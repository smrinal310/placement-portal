from flask import Flask
from flask_jwt_extended import JWTManager

from .apis.admin import admin_bp
from .apis.auth import auth_bp
from .config import Config
from .helpers.utils import create_admin
from .models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        create_admin(app)
    return app


app = create_app()
