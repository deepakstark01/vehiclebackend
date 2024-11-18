# main.py
from flask import Flask, jsonify
from src.routes import auth_routes, user_routes, vehicle_routes
from src.config.database import get_db
from src.services.auth_service import AuthService
from src.services.user_service import UserService
import os
from flask_cors import CORS
from config import config_by_name


def create_app(config_name='dev'):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize CORS
    CORS(app)

    # Initialize database
    app.db = get_db()

    # Initialize services
    app.auth_service = AuthService(app.db)
    app.user_service = UserService(app.db)

    # Register blueprints
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')
    app.register_blueprint(user_routes.bp, url_prefix='/users')
    app.register_blueprint(vehicle_routes.bp, url_prefix='/vehicles')

    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to the API',
            'version': '1.0.0'
        })

    return app


def init_app():
    env = os.getenv('FLASK_ENV', 'dev')
    app = create_app(env)

    print(f"Running in {env} mode")
    print(f"MongoDB URI: {app.config['MONGO_URI']}")
    print(f"Debug Mode: {app.config['DEBUG']}")

    return app


if __name__ == '__main__':
    app = init_app()
    port = int(os.getenv('PORT', 80))
    app.run(host='0.0.0.0', port=port)