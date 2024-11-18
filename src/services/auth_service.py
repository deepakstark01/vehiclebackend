from src.models.user_model import User
from datetime import datetime, timedelta
import jwt
from flask import current_app

from bson import ObjectId
import logging
from typing import Dict, Any


class AuthService:
    def __init__(self, db):
        self.db = db
        self.users_collection = db.users
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def register_user(self, first_name, last_name, username, email, password):
        try:
            # Input validation
            if not all([first_name, last_name, username, email, password]):
                return None, "All fields are required"

            # Validate email format
            if '@' not in email or '.' not in email:
                return None, "Invalid email format"

            # Validate password length
            if len(password) < 6:
                return None, "Password must be at least 6 characters long"

            # Check if user already exists
            existing_user = self.users_collection.find_one(
                {"$or": [{"username": username}, {"email": email}]}
            )
            if existing_user:
                if existing_user.get('username') == username:
                    return None, "Username already exists"
                return None, "Email already exists"

            # Create new user
            role = 'user'
            user = User(first_name, last_name, role, username, email, password)
            user_data = user.to_dict()
            user_data['password_hash'] = user.password_hash

            # Insert into database
            result = self.users_collection.insert_one(user_data)

            # Prepare response
            response_data = user_data.copy()
            response_data['_id'] = str(result.inserted_id)
            del response_data['password_hash']

            self.logger.info(f"User registered successfully: {username}")
            return response_data, None

        except Exception as e:
            self.logger.error(f"Error in register_user: {str(e)}")
            return None, f"Registration failed: {str(e)}"

    def login_user(self, username, password):
        try:
            # Find user
            user_data = self.users_collection.find_one({"username": username})
            if not user_data:
                return None, "User not found"

            # Check password
            user = User(
                user_data['first_name'],
                user_data['last_name'],
                user_data['username'],
                user_data['email'],
                ''
            )
            user.password_hash = user_data['password_hash']

            if not user.check_password(password):
                self.logger.warning(f"Invalid password attempt for user: {username}")
                return None, "Invalid password"

            # Convert ObjectId to string
            user_data['_id'] = str(user_data['_id'])

            # Generate token
            token = self.generate_token(user_data)

            # Prepare response
            response_data = user.to_dict()
            response_data['_id'] = user_data['_id']

            self.logger.info(f"User logged in successfully: {username}")
            return {
                "token": token,
                "user": response_data,
                "message": "Login successful"
            }, None

        except Exception as e:
            self.logger.error(f"Error in login_user: {str(e)}")
            return None, f"Login failed: {str(e)}"

    # src/services/auth_service.py

    def generate_token(self, user_data: Dict[str, Any]) -> str:
        try:
            payload = {
                'user_id': str(user_data['_id']),
                'username': user_data['username'],
                'full_name': f"{user_data['first_name']} {user_data['last_name']}",
                'exp': datetime.utcnow() + timedelta(days=1),
                'iat': datetime.utcnow()
            }
            return jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            self.logger.error(f"Error generating token: {str(e)}")
            raise
    # def generate_token(self, user_data):
    #     try:
    #         payload = {
    #             'user_id': str(user_data['_id']),
    #             'username': user_data['username'],
    #             'full_name': f"{user_data['first_name']} {user_data['last_name']}",
    #             'exp': datetime.utcnow() + timedelta(days=1),
    #             'iat': datetime.utcnow()
    #         }
    #         token = jwt.encode(
    #             payload,
    #             current_app.config['SECRET_KEY'],
    #             algorithm='HS256'
    #         )
    #         return token
    #
    #     except Exception as e:
    #         self.logger.error(f"Error generating token: {str(e)}")
    #         raise

    def verify_token(self, token):
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
        except Exception as e:
            self.logger.error(f"Error verifying token: {str(e)}")
            return None, "Token verification failed"

    def get_user_by_id(self, user_id):
        try:
            obj_id = ObjectId(user_id)
            user_data = self.users_collection.find_one({"_id": obj_id})

            if user_data:
                user_data['_id'] = str(user_data['_id'])
                del user_data['password_hash']
                return user_data

            return None

        except Exception as e:
            self.logger.error(f"Error in get_user_by_id: {str(e)}")
            return None

    def update_user(self, user_id, update_data):
        try:
            # Remove sensitive fields from update data
            if 'password_hash' in update_data:
                del update_data['password_hash']
            if '_id' in update_data:
                del update_data['_id']

            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )

            if result.modified_count:
                return self.get_user_by_id(user_id)
            return None

        except Exception as e:
            self.logger.error(f"Error in update_user: {str(e)}")
            return None
