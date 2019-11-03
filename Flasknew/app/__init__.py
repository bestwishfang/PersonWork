import pymysql

from flask import Flask
from flask_restful import Api
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy


pymysql.install_as_MySQLdb()

csrf = CSRFProtect()
models = SQLAlchemy()
api = Api()


def create():
    app = Flask(__name__)
    app.config.from_object('settings.Config')
    models.init_app(app)
    # csrf.init_app(app)
    api.init_app(app)

    from .main import main
    app.register_blueprint(main)
    return app