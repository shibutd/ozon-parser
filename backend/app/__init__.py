from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config


db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from .commands import cmd_bp
    app.register_blueprint(cmd_bp, cli_group=None)

    return app
