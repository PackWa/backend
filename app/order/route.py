from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.auth.auth import token_required
from app.order.models import Order
from app.services.order_service import OrderService
from app.order.schemas import OrderSchema

order_bp = Blueprint('order', __name__, url_prefix='/order')

@order_bp.route('/', methods=['POST'])
@token_required
def create_order(user_id):
    data = request.json
    if data is None:
        return jsonify({"error": "No data"}), 400

    schema = OrderSchema()
    try:
        validated_data = schema.load(data)  # Валидация + преобразование
    except ValidationError as err:
        return jsonify(err.messages), 400

    order, errors = OrderService.create_order(user_id, validated_data)
    if errors:
        return jsonify(errors), 400

    return jsonify(order), 201

@order_bp.route('/', methods=['GET'])
@token_required
def get_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return jsonify(OrderSchema(many=True).dump(orders)), 200


@order_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(user_id, order_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user id"}), 400

    order = Order.query.get(order_id)

    if not order or order.user_id != user_id:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify(OrderSchema().dump(order)), 200


@order_bp.route('/<int:order_id>', methods=['PUT'])
@token_required
def update_order(user_id, order_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user id"}), 400
    order = Order.query.get(order_id)

    # Проверка прав доступа
    if not order or order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    # Валидация
    data = request.json
    schema = OrderSchema(partial=True)
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400

    print()

    # Обновление
    updated_order, errors = OrderService.update_order(user_id, order, data)
    if errors:
        return jsonify(errors), 400

    return jsonify(updated_order), 200


@order_bp.route('/<int:order_id>', methods=['DELETE'])
@token_required
def delete_order(user_id, order_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user id"}), 400
    order = Order.query.get(order_id)

    if not order or order.user_id != user_id:
        return jsonify({'error': 'Order not found'}), 404

    result, status = OrderService.delete_order(order)
    return jsonify(result), status