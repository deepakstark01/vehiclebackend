# src/routes/auth_routes.py
from flask import Blueprint, request
from src.controllers.auth_controller import AuthController

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['POST'])
def signup():
    return AuthController.signup(request.get_json())

@bp.route('/login', methods=['POST'])
def login():
    return AuthController.login(request.get_json())