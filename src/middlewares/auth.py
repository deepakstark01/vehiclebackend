# src/middlewares/auth.py
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from typing import Callable
from bson import ObjectId


def token_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        # Check if Authorization header exists
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        try:
            # Extract token from "Bearer <token>"
            if ' ' not in auth_header:
                return jsonify({'error': 'Invalid token format. Use "Bearer <token>"'}), 401

            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                return jsonify({'error': 'Invalid authentication scheme. Use "Bearer"'}), 401

            if not token:
                return jsonify({'error': 'Token is missing'}), 401

            # Verify token
            try:
                payload = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401

            # Get user from database
            current_user = current_app.db.users.find_one({'_id': ObjectId(payload['user_id'])})
            if not current_user:
                return jsonify({'error': 'User not found'}), 401

            # Check if user is active
            if not current_user.get('is_active', True):
                return jsonify({'error': 'User account is inactive'}), 401

            # Convert ObjectId to string
            current_user['_id'] = str(current_user['_id'])

            # Call the original function with current_user
            return f(current_user, *args, **kwargs)

        except Exception as e:
            current_app.logger.error(f"Token verification error: {str(e)}")
            return jsonify({'error': f'Token verification failed: {str(e)}'}), 401

    return decorated