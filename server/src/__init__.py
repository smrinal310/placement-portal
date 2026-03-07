from flask import Flask
from flask_jwt_extended import JWTManager

from .config import Config
from .helpers.utils import create_admin
from .models import db
from .routes.auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()
        create_admin(app)
    return app


app = create_app()
