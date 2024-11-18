# src/controllers/auth_controller.py
from flask import jsonify, current_app
from src.services.auth_service import AuthService

class AuthController:
    @staticmethod
    def signup(data):
        required_fields = ['first_name', 'last_name', 'username', 'email', 'password']
        if not all(key in data for key in required_fields):
            return jsonify({
                'error': f'Missing required fields. Required fields are: {", ".join(required_fields)}'
            }), 400

        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        user, error = current_app.auth_service.register_user(
            data['first_name'],
            data['last_name'],
            data['username'],
            data['email'],
            data['password']
        )

        if error:
            return jsonify({'error': error}), 400

        return jsonify({
            'message': 'User created successfully',
            'user': user
        }), 201

    @staticmethod
    def login(data):
        if not all(key in data for key in ['username', 'password']):
            return jsonify({'error': 'Missing username or password'}), 400

        result, error = current_app.auth_service.login_user(
            data['username'],
            data['password']
        )

        if error:
            return jsonify({'error': error}), 401

        return jsonify(result), 200
