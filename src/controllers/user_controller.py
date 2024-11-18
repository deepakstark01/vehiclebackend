# src/controllers/user_controller.py
from flask import jsonify, current_app
from typing import Dict, Any, Tuple
import logging
import math
from bson import ObjectId


class UserController:
    @classmethod
    def get_profile(cls, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Get user profile details"""
        try:
            user_service = current_app.user_service
            user_id = str(current_user['_id'])

            # Get full user profile from service
            user_profile = user_service.get_user_by_id(user_id)

            if not user_profile:
                return jsonify({'error': 'User not found'}), 404

            return jsonify({
                'status': 'success',
                'data': user_profile
            }), 200

        except Exception as e:
            logging.error(f"Error in get_profile: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch profile'
            }), 500

    @classmethod
    def update_profile(cls, current_user: Dict[str, Any], data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Update user profile"""
        try:
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'No data provided'
                }), 400

            # Validate input data
            valid_fields = [
                'phone', 'address', 'city', 'state',
                'country', 'pincode', 'bio',
                'date_of_birth', 'gender', 'social_links'
            ]
            update_data = {k: v for k, v in data.items() if k in valid_fields}

            if not update_data:
                return jsonify({
                    'status': 'error',
                    'message': 'No valid fields to update'
                }), 400

            user_service = current_app.user_service
            user_id = str(current_user['_id'])

            # Update profile using service
            updated_user, error = user_service.update_profile(user_id, update_data)

            if error:
                return jsonify({
                    'status': 'error',
                    'message': error
                }), 400

            return jsonify({
                'status': 'success',
                'message': 'Profile updated successfully',
                'data': updated_user
            }), 200

        except Exception as e:
            logging.error(f"Error in update_profile: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to update profile'
            }), 500

    @classmethod
    def update_avatar(cls, current_user: Dict[str, Any], data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Update user avatar"""
        try:
            if 'avatar_url' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'Avatar URL is required'
                }), 400

            user_service = current_app.user_service
            user_id = str(current_user['_id'])

            success, error = user_service.update_avatar(user_id, data['avatar_url'])

            if not success:
                return jsonify({
                    'status': 'error',
                    'message': error or 'Failed to update avatar'
                }), 400

            return jsonify({
                'status': 'success',
                'message': 'Avatar updated successfully',
                'data': {'avatar_url': data['avatar_url']}
            }), 200

        except Exception as e:
            logging.error(f"Error in update_avatar: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to update avatar'
            }), 500

    @classmethod
    def change_password(cls, current_user: Dict[str, Any], data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Change user password"""
        try:
            required_fields = ['current_password', 'new_password']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'status': 'error',
                    'message': 'Current password and new password are required'
                }), 400

            if len(data['new_password']) < 6:
                return jsonify({
                    'status': 'error',
                    'message': 'New password must be at least 6 characters long'
                }), 400

            user_service = current_app.user_service
            user_id = str(current_user['_id'])

            success, error = user_service.update_password(
                user_id,
                data['current_password'],
                data['new_password']
            )

            if not success:
                return jsonify({
                    'status': 'error',
                    'message': error or 'Failed to update password'
                }), 400

            return jsonify({
                'status': 'success',
                'message': 'Password updated successfully'
            }), 200

        except Exception as e:
            logging.error(f"Error in change_password: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to change password'
            }), 500

    @classmethod
    def create_user(cls, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Create a new user"""
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role']
            if not all(key in data for key in required_fields):
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required fields. Required fields are: {", ".join(required_fields)}'
                }), 400

            # Additional validation
            if len(data['password']) < 6:
                return jsonify({
                    'status': 'error',
                    'message': 'Password must be at least 6 characters long'
                }), 400

            if not data['email'].strip() or '@' not in data['email']:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid email format'
                }), 400

            # Validate role
            valid_roles = ['user', 'admin']
            if data['role'] not in valid_roles:
                return jsonify({
                    'status': 'error',
                    'message': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
                }), 400

            user_service = current_app.user_service
            user, error = user_service.create_user(data)

            if error:
                return jsonify({
                    'status': 'error',
                    'message': error
                }), 400

            return jsonify({
                'status': 'success',
                'message': 'User created successfully',
                'data': user
            }), 201

        except Exception as e:
            logging.error(f"Error in create_user: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to create user'
            }), 500

    # Fix list_users to match class method pattern
    @classmethod
    def list_users(cls, page: int, limit: int) -> Tuple[Dict[str, Any], int]:
        """
        List users with pagination

        Args:
            page: Page number (starts from 1)
            limit: Number of items per page
        """
        try:
            # Validate pagination parameters
            page = max(1, page)  # Ensure page is at least 1
            limit = max(1, min(limit, 100))  # Limit between 1 and 100

            user_service = current_app.user_service
            users, total_count = user_service.get_all_users_paginated(page, limit)

            # Calculate pagination metadata
            total_pages = math.ceil(total_count / limit)
            has_next = page < total_pages
            has_prev = page > 1

            return jsonify({
                'status': 'success',
                'data': {
                    'users': users,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total_items': total_count,
                        'total_pages': total_pages,
                        'has_next': has_next,
                        'has_prev': has_prev,
                        'next_page': page + 1 if has_next else None,
                        'prev_page': page - 1 if has_prev else None
                    }
                }
            }), 200

        except Exception as e:
            logging.error(f"Error in list_users: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch users'
            }), 500