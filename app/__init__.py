import locale
from flask import Flask, Blueprint
from flask_ckeditor import CKEditor
from flask_restful import Api

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, AnonymousUserMixin

import pymorphy3


class Anonymous(AnonymousUserMixin):
    username = "Guest"
    studios = []


app = Flask(__name__)
app.config.from_object(Config)

ckeditor = CKEditor(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager()
login.init_app(app)

login.login_view = 'login'

morph = pymorphy3.MorphAnalyzer()
locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian"
)

from app import routes, models
