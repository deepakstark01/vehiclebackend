# src/routes/user_routes.py
from flask import Blueprint, request, current_app , jsonify
from src.controllers.user_controller import UserController
from src.middlewares.auth import token_required
from src.middlewares.role_check import admin_required

bp = Blueprint('users', __name__)

# Profile Routes
@bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile"""
    return UserController.get_profile(current_user)

@bp.route('/profile/update', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user basic profile"""
    return UserController.update_profile(current_user, request.get_json())

@bp.route('/profile/avatar', methods=['PUT'])
@token_required
def update_avatar(current_user):
    """Update user avatar"""
    return UserController.update_avatar(current_user, request.get_json())

@bp.route('/profile/password', methods=['PUT'])
@token_required
def change_password(current_user):
    """Change user password"""
    return UserController.change_password(current_user, request.get_json())


# Admin Routes
@bp.route('/list', methods=['GET'])
@token_required
@admin_required
def list_users(current_use):
    """Get all users with pagination (admin only)"""
    try:
        # Get and validate pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        # Ensure positive values
        page = max(1, page)
        limit = max(1, min(limit, 100))  # Cap limit at 100

        return UserController.list_users(page, limit)

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': 'Invalid pagination parameters'
        }), 400

@bp.route('/createuser', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    """Create a new user (admin only)"""
    return UserController.create_user(request.get_json())

