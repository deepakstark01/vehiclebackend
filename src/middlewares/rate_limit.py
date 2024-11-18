# src/middlewares/rate_limit.py

from functools import wraps
from flask import request, jsonify, current_app

def check_rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get API key from header or request body
            api_key = request.headers.get('X-API-Key')
            if not api_key and request.is_json:
                api_key = request.json.get('api_key')

            if not api_key:
                return jsonify({
                    'status': 'error',
                    'message': 'API key is required'
                }), 401

            # Validate and get key data
            is_valid, key_data, error = current_app.api_key_service.validate_api_key(api_key)

            if not is_valid or not key_data:
                return jsonify({
                    'status': 'error',
                    'message': error or 'Invalid API key'
                }), 401

            # Check rate limit
            is_allowed, error = current_app.api_key_service.check_rate_limit(key_data)

            if not is_allowed:
                return jsonify({
                    'status': 'error',
                    'message': error,
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'rate_limit': {
                        'plan': key_data['plan'],
                        'limit': {
                            'free': '100 requests per minute',
                            'basic': '200 requests per minute',
                            'premium': '600 requests per minute',
                            'enterprise': '1 request per second'
                        }.get(key_data['plan'], '100 requests per minute')
                    }
                }), 429

            # Pass key_data to the route
            return f(key_data, *args, **kwargs)

        except Exception as e:

            current_app.logger.error(f"Rate limit check error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Rate limit check failed'
            }), 500

    return decorated