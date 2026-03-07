from flask import Flask

from .config import Config
from .helpers.utils import create_admin
from .models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_admin(app)
    return app


app = create_app()
