
# src/services/user_service.py
from typing import Dict, Any, Tuple, Optional, List
from bson import ObjectId
import logging
from datetime import datetime
from ..models.user_model import User, UserProfile

class UserService:
    def __init__(self, db):
        self.db = db
        self.users_collection = db.users
        self.logger = logging.getLogger(__name__)

    def create_user(self, user_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            # Create user instance
            user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']

            )

            # Convert to dictionary for storage
            user_dict = user.to_dict()
            user_dict['password_hash'] = user.password_hash

            # Insert into database
            result = self.users_collection.insert_one(user_dict)
            user_dict['_id'] = str(result.inserted_id)
            del user_dict['password_hash']

            return user_dict, None
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            return None, str(e)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                del user['password_hash']
                return user
            return None
        except Exception as e:
            self.logger.error(f"Error fetching user: {str(e)}")
            return None

    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            # Validate and clean profile data
            valid_fields = [
                'phone', 'address', 'city', 'state', 'country', 'pincode',
                'bio', 'date_of_birth', 'gender', 'social_links'
            ]
            update_data = {'profile.' + k: v for k, v in profile_data.items() if k in valid_fields}

            if not update_data:
                return None, "No valid fields to update"

            # Update user profile
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )

            if result.modified_count:
                updated_user = self.get_user_by_id(user_id)
                return updated_user, None

            return None, "Profile update failed"
        except Exception as e:
            self.logger.error(f"Error updating profile: {str(e)}")
            return None, str(e)

    def update_avatar(self, user_id: str, avatar_url: str) -> Tuple[bool, Optional[str]]:
        try:
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'profile.avatar_url': avatar_url}}
            )
            return result.modified_count > 0, None
        except Exception as e:
            self.logger.error(f"Error updating avatar: {str(e)}")
            return False, str(e)

    def update_password(self, user_id: str, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        try:
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return False, "User not found"

            # Verify current password
            temp_user = User(
                user['first_name'],
                user['last_name'],
                user['username'],
                user['email']
            )
            temp_user.password_hash = user['password_hash']

            if not temp_user.check_password(current_password):
                return False, "Current password is incorrect"

            # Update to new password
            new_user = User('', '', '', '', new_password)
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password_hash': new_user.password_hash}}
            )

            return result.modified_count > 0, None
        except Exception as e:
            self.logger.error(f"Error updating password: {str(e)}")
            return False, str(e)

    def update_last_login(self, user_id: str) -> bool:
        try:
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating last login: {str(e)}")
            return False


    def get_all_users_paginated(self, page: int, limit: int) -> Tuple[List[Dict[str, Any]], int]:
        try:
            # Calculate skip value for pagination
            skip = (page - 1) * limit

            # Get total count first
            total_count = self.users_collection.count_documents({})

            # Get paginated users
            users_cursor = self.users_collection.find({}) \
                .skip(skip) \
                .limit(limit) \
                .sort('created_at', -1)  # Sort by creation date, newest first

            # Convert cursor to list and process users
            users = []
            for user in users_cursor:
                # Remove sensitive data and convert ObjectId
                user['_id'] = str(user['_id'])
                if 'password_hash' in user:
                    del user['password_hash']
                users.append(user)

            return users, total_count

        except Exception as e:
            self.logger.error(f"Error fetching paginated users: {str(e)}")
            return [], 0