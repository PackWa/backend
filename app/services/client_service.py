from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.client.models import Client
from app.client.schemas import ClientSchema


class ClientService:
    @staticmethod
    def create_client(user_id, client_data):
        schema = ClientSchema()
        errors = schema.validate(client_data)
        if errors:
            return None, errors

        try:
            new_client = Client(
                user_id=user_id,
                first_name=client_data['first_name'],
                last_name=client_data['last_name'],
                phone=client_data.get('phone')
            )

            db.session.add(new_client)
            db.session.commit()
            return schema.dump(new_client), None

        except IntegrityError as e:
            db.session.rollback()
            return None, {'database_error': 'Database integrity error'}
        except Exception as e:
            db.session.rollback()
            return None, {'error': str(e)}

    @staticmethod
    def get_all_clients(user_id):
        clients = Client.query.filter_by(user_id=user_id).all()
        return ClientSchema(many=True).dump(clients), None

    @staticmethod
    def update_client(client, update_data):
        if not client:
            return None, {'error': 'Client not found'}

        # Список допустимых ключей для обновления
        valid_fields = ["first_name", "last_name", "phone"]

        # Проверяем, что хотя бы один ключ из valid_fields присутствует в update_data
        if not any(field in update_data for field in valid_fields):
            return None, {
                'error': 'Invalid update keys. At least one of "first_name", "last_name", or "phone" is required.'}

        try:
            for key, value in update_data.items():
                if hasattr(client, key):  # Обновляем только допустимые поля
                    setattr(client, key, value)

            db.session.commit()
            return ClientSchema().dump(client), None

        except IntegrityError as e:
            db.session.rollback()
            return None, {'database_error': 'Database integrity error'}
        except Exception as e:
            db.session.rollback()
            return None, {'error': str(e)}

    @staticmethod
    def delete_client(client):
        if not client:
            return {'error': 'Client not found'}, 404

        try:
            db.session.delete(client)
            db.session.commit()
            return {'message': 'Client deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500