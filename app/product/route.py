from flask import Blueprint, request, jsonify, send_from_directory, current_app

from app.product.models import Product
from app.services.product_service import ProductService
from app.product.schemas import ProductSchema
import os

from app.auth.auth import decode_jwt, token_required

product_bp = Blueprint('product', __name__, url_prefix='/product')


@product_bp.route('/', methods=['POST'])
@token_required
def create_product(user_id):

    # Обрабатываем multipart/form-data
    data = request.form.to_dict()
    print(data)
    data['user_id'] = user_id
    photo_file = request.files.get('photo')

    # Валидация данных
    schema = ProductSchema()
    errors = schema.validate(data)
    print(errors)

    if errors:
        return jsonify(errors), 400

    # Создание продукта
    product, errors = ProductService.create_product(
        user_id=user_id,
        product_data=data,
        photo_file=photo_file
    )

    if errors:
        return jsonify(errors), 400 if 'photo' not in errors else 400
    return jsonify(product), 201


@product_bp.route('/', methods=['GET'])
@token_required
def get_products(user_id):
    products = Product.query.filter_by(user_id=user_id).all()
    return jsonify(ProductSchema(many=True).dump(products)), 200


@product_bp.route('/<int:product_id>', methods=['PUT'])
@token_required
def update_product(user_id, product_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user id'}), 400

    product = Product.query.get(product_id)
    print(product)
    if not product or product.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    if request.is_json:
        data = request.json
        photo_file = None  # Для обработки файла изображения, если он не передается в JSON
    else:
        # Обработка данных формы, если запрос не в формате JSON
        data = request.form.to_dict()
        photo_file = request.files.get('photo')

    if not data and not photo_file:
        return jsonify({'error': 'No data provided'}), 400

    schema = ProductSchema(partial=True)
    if data:
        errors = schema.validate(data)
        if errors:
            return jsonify(errors), 400

    updated_product, errors = ProductService.update_product(
        product=product,
        update_data=data,
        photo_file=photo_file
    )

    if errors:
        return jsonify(errors), 400
    return jsonify(updated_product), 200


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(user_id, product_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user id'}), 400
    product = Product.query.get(product_id)

    if not product or product.user_id != user_id:
        return jsonify({'error': 'Product not found'}), 404

    result, status = ProductService.delete_product(product_id)
    return jsonify(result), status


@product_bp.route('/photo/<filename>', methods=['GET'])
@token_required
def get_photo(user_id, filename):
    print(int(user_id))
    print("work")
    print(filename)
    return send_from_directory(
        directory=current_app.config['UPLOAD_FOLDER'],
        path=filename,
        as_attachment=False
    )
