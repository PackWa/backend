from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.user.models import User
from app.user.schemas import UserSchema
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:
    @staticmethod
    def create_user(user_data):
        schema = UserSchema()
        errors = schema.validate(user_data)
        if errors:
            return None, errors

        # Проверка уникальности email и телефона
        if User.query.filter_by(email=user_data['email']).first():
            return None, {'email': 'Email already registered'}

        if User.query.filter_by(phone=user_data['phone']).first():
            return None, {'phone': 'Phone already registered'}

        try:
            hashed_password = generate_password_hash(user_data['password'])
            new_user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                email=user_data['email'],
                password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()
            return schema.dump(new_user), None

        except IntegrityError as e:
            db.session.rollback()
            return None, {'database_error': 'Database integrity error'}
        except Exception as e:
            db.session.rollback()
            return None, {'database_error': str(e)}

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return None
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        db.session.delete(user)
        try:
            db.session.commit()
            return {'message': 'User deleted'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500