# src/middlewares/api_key_auth.py
from functools import wraps
from flask import request, jsonify, current_app


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API key is required'
            }), 401

        is_valid, key_data, error = current_app.api_key_service.validate_api_key(api_key)

        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error
            }), 401

        return f(key_data, *args, **kwargs)

    return decorated