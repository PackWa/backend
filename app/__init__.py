# app/__init__.py
import os
from datetime import datetime
from uuid import uuid4

from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)

    CORS(app)

    # Регистрация моделей
    from app.user import models as user_models
    from app.client import models as client_models
    from app.product import models as product_models
    from app.order import models as order_models

    with app.app_context():
        db.create_all()

    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'product_photos')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['MAX_FILE_SIZE'] = 16 * 1024 * 1024  # 16MB

    # Создаем папку для загрузок, если ее нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # регистрация blueprint
    from app.user.route import user_bp
    from app.product.route import product_bp
    from app.client.route import client_bp
    from app.order.route import order_bp

    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(order_bp, url_prefix='/order')

    # Создание таблиц при первом запуске
    with app.app_context():
        db.create_all()

    return app