import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-for-development'
    DEBUG = False

    # MongoDB config
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/your_database'

    # JWT config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    # Application config
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # CORS settings
    CORS_HEADERS = 'Content-Type'


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')



class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MONGO_URI = "mongodb+srv://rohit45deepak:Id2xXca4Z0qBwTzW@cluster0.rmxss.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


# Dictionary to easily select config
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestingConfig
}
