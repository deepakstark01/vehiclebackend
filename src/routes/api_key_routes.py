# src/routes/api_key_routes.py
from flask import Blueprint, request, jsonify, current_app
from src.middlewares.auth import token_required
from src.middlewares.role_check import admin_required
from datetime import datetime

bp = Blueprint('api_keys', __name__)


@bp.route('/create', methods=['POST'])
@token_required
def create_api_key(current_user):
    """Create a new API key"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400

        required_fields = ['name', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': f'Required fields: {", ".join(required_fields)}'
            }), 400

        # Create API key
        key_data, error = current_app.api_key_service.create_api_key(
            str(current_user['_id']),
            data['name'],
        )

        if error:
            return jsonify({
                'status': 'error',
                'message': error
            }), 400

        return jsonify({
            'status': 'success',
            'message': 'API key created successfully',
            'data': key_data
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@bp.route('/verify', methods=['POST'])
def verify_api_key():
    """Verify API key from request body"""
    try:
        data = request.get_json()

        if not data or 'api_key' not in data:
            return jsonify({
                'status': 'error',
                'message': 'API key is required in request body'
            }), 400

        is_valid, key_data, error = current_app.api_key_service.validate_api_key(data['api_key'])

        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error or 'Invalid API key',
                'is_valid': False
            }), 401

        return jsonify({
            'status': 'success',
            'data': {
                'is_valid': True,
                'plan': key_data['plan'],
                'daily_limit': key_data['daily_limit'],
                'remaining_calls': key_data['daily_limit'] - key_data['daily_usage']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@bp.route('/revoke', methods=['POST'])
@token_required
def revoke_api_key(current_user):
    """Revoke API key from request body"""
    try:
        data = request.get_json()

        if not data or 'api_key' not in data:
            return jsonify({
                'status': 'error',
                'message': 'API key is required in request body'
            }), 400

        success, error = current_app.api_key_service.revoke_api_key(
            str(current_user['_id']),
            data['api_key']
        )

        if not success:
            return jsonify({
                'status': 'error',
                'message': error or 'Failed to revoke API key'
            }), 400

        return jsonify({
            'status': 'success',
            'message': 'API key revoked successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@bp.route('/status', methods=['POST'])
@token_required
def get_api_key_status(current_user):
    """Get API key status from request body"""
    try:
        data = request.get_json()

        if not data or 'api_key' not in data:
            return jsonify({
                'status': 'error',
                'message': 'API key is required in request body'
            }), 400

        is_valid, key_data, error = current_app.api_key_service.validate_api_key(data['api_key'])

        if not is_valid and not key_data:
            return jsonify({
                'status': 'error',
                'message': error or 'Invalid API key'
            }), 404

        return jsonify({
            'status': 'success',
            'data': {
                'api_key': key_data['api_key'],
                'name': key_data['name'],
                'plan': key_data['plan'],
                'is_active': key_data['is_active'],
                'usage': {
                    'daily_usage': key_data['daily_usage'],
                    'daily_limit': key_data['daily_limit'],
                    'remaining_calls': key_data['daily_limit'] - key_data['daily_usage'],
                    'last_used': key_data['last_used'].isoformat() if key_data['last_used'] else None,
                    'last_reset': key_data['last_reset'].isoformat() if key_data['last_reset'] else None
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@bp.route('/list', methods=['POST'])
@token_required
def list_api_keys(current_user):
    """List all API keys with pagination from request body"""
    try:
        data = request.get_json()
        page = data.get('page', 1)
        limit = min(data.get('limit', 10), 50)  # Cap at 50

        keys = current_app.api_key_service.get_user_api_keys(str(current_user['_id']))

        # Simple pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_keys = keys[start_idx:end_idx]

        return jsonify({
            'status': 'success',
            'data': {
                'keys': paginated_keys,
                'total': len(keys),
                'page': page,
                'limit': limit,
                'total_pages': (len(keys) + limit - 1) // limit,
                'remaining_slots': 5 - len(keys)  # Based on 5 keys limit
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500