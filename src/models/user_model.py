
# src/models/user_model.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Dict, Any, Optional

class User:
    def __init__(self, first_name: str, last_name:  str, role :str, username: str, email: str, password: Optional[str] = None):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.created_at = datetime.utcnow()
        self.full_name = f"{first_name} {last_name}"
        self.role = role
        self.is_active = True
        self.last_login = None
        self.profile = UserProfile()

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "role": self.role,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "profile": self.profile.to_dict()
        }

class UserProfile:
    def __init__(self):
        self.phone = None
        self.address = None
        self.city = None
        self.state = None
        self.country = None
        self.pincode = None
        self.bio = None
        self.avatar_url = None
        self.date_of_birth = None
        self.gender = None
        self.social_links = {
            "facebook": None,
            "twitter": None,
            "linkedin": None,
            "instagram": None
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "pincode": self.pincode,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "social_links": self.social_links
        }
