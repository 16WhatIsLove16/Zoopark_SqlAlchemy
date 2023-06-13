from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

"""Конфигурация приложения и подключение к БД"""
app = Flask(__name__)
app.secret_key = 'some secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zoopark2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = SQLAlchemy(app)
manager = LoginManager(app)

from sweater import routes, models

# Создание БД, если её не существует
# with app.app_context():
#     db.create_all()
