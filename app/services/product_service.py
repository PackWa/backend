import os
from datetime import datetime
from uuid import uuid4

from werkzeug.utils import secure_filename
from flask import current_app

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.product.models import Product
from app.product.schemas import ProductSchema


class ProductService:
    @staticmethod
    def _allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    @staticmethod
    def create_product(user_id, product_data, photo_file=None):
        photo_filename = None
        try:

            # Проверка уникальности имени
            if Product.query.filter_by(user_id=user_id, title=product_data['title']).first():
                return None, {'title': 'Product`s title already exists for this user'}

            # Обработка фото
            if photo_file:
                filename, error = ProductService.save_photo(photo_file)
                if error:
                    return None, {'photo': error}
                photo_filename = filename

            # Создание продукта
            new_product = Product(
                user_id=user_id,
                title=product_data['title'],
                description=product_data.get('description'),
                price=product_data['price'],
                photo=photo_filename
            )

            db.session.add(new_product)
            db.session.commit()

            return ProductSchema().dump(new_product), None

        except IntegrityError:
            # Удаляем сохраненный файл при ошибке
            if photo_filename:
                ProductService.delete_photo(photo_filename)
            db.session.rollback()
            return None, {'title': 'Product`s title already exists for this user'}
        except Exception as e:
            if photo_filename:
                ProductService.delete_photo(photo_filename)
            db.session.rollback()
            return None, {'error': str(e)}

    @staticmethod
    def save_photo(file):
        if not file or file.filename == '':
            return None, 'No selected file'

        if not ProductService._allowed_file(file.filename):
            return None, 'File type not allowed'

        if file.content_length > current_app.config['MAX_FILE_SIZE']:
            return None, 'File too large'

        # Генерируем уникальное имя файла
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}.{ext}"
        filename = secure_filename(unique_name)

        try:
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            return filename, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def delete_photo(filename):
        if not filename:
            return
        try:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            current_app.logger.error(f"Error deleting file {filename}: {str(e)}")

    @staticmethod
    def update_product(product, update_data, photo_file=None):
        new_photo = None
        try:
            if not product:
                return None, {'error': 'Product not found'}

            old_photo = product.photo

            # Проверка, что хотя бы одно из полей для обновления предоставлено
            if not any(field in update_data for field in ['title', 'price', 'description', 'photo']) and not photo_file:
                return None, {'error': 'No data provided for update'}

            # Обработка новой фотографии
            if photo_file:
                filename, error = ProductService.save_photo(photo_file)
                if error:
                    return None, {'photo': error}
                new_photo = filename
                update_data['photo'] = new_photo

            # Проверка уникальности имени
            if 'title' in update_data:
                existing = Product.query.filter(
                    Product.user_id == product.user_id,
                    Product.title == update_data['title'],
                    Product.id != product.id
                ).first()
                if existing:
                    if new_photo:
                        ProductService.delete_photo(new_photo)
                    return None, {'title': 'Product title already exists for this user'}

            # Обновление полей, при этом если данных нет, сохраняем старые значения
            for key, value in update_data.items():
                if hasattr(product, key):
                    setattr(product, key, value)

            # Если каких-то полей не было, восстанавливаем их старые значения
            for key in ['title', 'description', 'price', 'photo']:
                if key not in update_data:
                    setattr(product, key, getattr(product, key))  # сохраняем старое значение

            # Коммитим изменения в БД
            db.session.commit()

            # Удаляем старую фотографию после успешного обновления
            if new_photo and old_photo:
                ProductService.delete_photo(old_photo)

            return ProductSchema().dump(product), None

        except IntegrityError:
            if new_photo:
                ProductService.delete_photo(new_photo)
            db.session.rollback()
            return None, {'title': 'Product`s title already exists for this user'}
        except Exception as e:
            if new_photo:
                ProductService.delete_photo(new_photo)
            db.session.rollback()
            return None, {'error': str(e)}

    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            return {'error': 'Product not found'}, 404

        photo_to_delete = product.photo
        try:
            db.session.delete(product)
            db.session.commit()
            # Удаляем файл после успешного удаления из БД
            if photo_to_delete:
                ProductService.delete_photo(photo_to_delete)
            return {'message': 'Product deleted'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500