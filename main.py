# main.py
from flask import Flask, jsonify , Blueprint, send_from_directory
from src.routes import auth_routes, user_routes, vehicle_routes , api_key_routes
from src.config.database import get_db
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.services.api_key_service import APIKeyService
import os
from flask_cors import CORS
from config import config_by_name


def create_app(config_name='dev'):
    app = Flask(__name__,  static_folder='dist')

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize CORS
    CORS(app)

    # Initialize database
    app.db = get_db()

    # Initialize services
    app.auth_service = AuthService(app.db)
    app.user_service = UserService(app.db)
    app.api_key_service = APIKeyService(app.db)

    # app.register_blueprint(auth_routes.bp, url_prefix='/auth')
    # app.register_blueprint(user_routes.bp, url_prefix='/users')
    # app.register_blueprint(vehicle_routes.bp, url_prefix='/vehicles')
    # app.register_blueprint(api_key_routes.bp, url_prefix='/api')

    api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

    # Register route blueprints under api_v1
    api_v1.register_blueprint(auth_routes.bp, url_prefix='/auth')
    api_v1.register_blueprint(user_routes.bp, url_prefix='/users')
    api_v1.register_blueprint(vehicle_routes.bp, url_prefix='/vehicles')
    api_v1.register_blueprint(api_key_routes.bp, url_prefix='/keys')

    # Register api_v1 blueprint
    app.register_blueprint(api_v1)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

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