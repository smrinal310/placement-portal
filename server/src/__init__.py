import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .apis.admin import admin_bp
from .apis.auth import auth_bp
from .apis.company import company_bp
from .apis.student import student_bp
from .config import Config
from .helpers.cache import cache
from .helpers.email import mail
from .helpers.utils import create_admin
from .jobs.celery_app import make_celery
from .models import db


def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="/static")
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    mail.init_app(app)
    cache.init_app(app)
    app.celery = make_celery(app)

    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
            "supports_credentials": True
        },
        r"/auth/*": {
            "origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
            "supports_credentials": True
        }
    })

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    # Ensure upload directories exist
    os.makedirs(
        app.config.get("EXPORTS_FOLDER", "static/uploads/exports"),
        exist_ok=True,
    )
    os.makedirs(
        app.config.get("REPORTS_FOLDER", "static/uploads/reports"),
        exist_ok=True,
    )

    with app.app_context():
        db.create_all()
        create_admin(app)
    return app
