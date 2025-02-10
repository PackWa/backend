from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

from ..auth.auth import generate_jwt, decode_jwt, token_required

from .models import User
from .schemas import UserSchema
from app.extensions import db
from ..services.user_service import UserService

user_bp = Blueprint('user', __name__, url_prefix='/user')
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@user_bp.route('/register', methods=['POST'])
def register():
    # Валидация входных данных
    schema = UserSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    try:
        user_data = request.json
        result, errors = UserService.create_user(user_data)

        if errors:
            return jsonify(errors), 400 if 'database_error' not in errors else 500

        response_data = {
            "id": result["id"],
            "email": result["email"],
            "first_name": result["first_name"],
            "last_name": result["last_name"],
            "phone": result["phone"]
        }
        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = UserService.authenticate(data.get('email'), data.get('password'))

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = generate_jwt(user.id)
    return jsonify({
        "access_token": access_token,
        "user": UserSchema().dump(user)
    }), 200


@user_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone
    }), 200


@user_bp.route('/delete', methods=['DELETE'])
@token_required
def delete_account(user_id):
    result, status = UserService.delete_user(user_id)

    if status != 200:
        return jsonify(result), status

    return jsonify({"message": "Account deleted successfully"}), 200