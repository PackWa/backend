from flask import Blueprint, request, jsonify
from app.auth.auth import token_required, decode_jwt
from app.client.models import Client
from app.client.schemas import ClientSchema
from app.services.client_service import ClientService

client_bp = Blueprint('client', __name__, url_prefix='/client')


@client_bp.route('/', methods=['POST'])
@token_required
def create_client(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user id'}), 400

    data = request.get_json()
    data['user_id'] = user_id

    client, errors = ClientService.create_client(user_id, data)
    if errors:
        return jsonify(errors), 400

    return jsonify(client), 201


@client_bp.route('/', methods=['GET'])
@token_required
def get_clients(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user id'}), 400

    clients, errors = ClientService.get_all_clients(user_id)
    if errors:
        return jsonify(errors), 400
    return jsonify(clients), 200


@client_bp.route('/<int:client_id>', methods=['GET'])
@token_required
def get_client(user_id, client_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user id'}), 400

    client, errors = ClientService.get_client(client_id)

    if errors:
        return jsonify(errors), 404
    if client['user_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(client), 200


@client_bp.route('/<int:client_id>', methods=['PUT'])
@token_required
def update_client(user_id, client_id):
    try:
        user_id = int(user_id)
        client_id = int(client_id)
    except ValueError:
        return jsonify({'error': 'Invalid user id'}), 400

    client = Client.query.get(client_id)

    if not client or client.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    data = request.json
    schema = ClientSchema(partial=True)
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400

    updated_client, errors = ClientService.update_client(client, data)

    if errors:
        return jsonify(errors), 400
    return jsonify(updated_client), 200


@client_bp.route('/<int:client_id>', methods=['DELETE'])
@token_required
def delete_client(user_id, client_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user id'}), 400

    client = Client.query.get(client_id)

    if not client or client.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    result, status = ClientService.delete_client(client)
    return jsonify(result), status