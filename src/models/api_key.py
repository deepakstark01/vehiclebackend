# src/models/api_key.py
from datetime import datetime
import secrets
from typing import Dict, Any

class APIKey:
    def __init__(self, user_id: str, name: str, plan: str = 'free', rate_limit_minutes: float = 1):
        self.api_key = self._generate_api_key()
        self.user_id = user_id
        self.name = name
        self.plan = plan
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.last_used = None
        self.daily_limit = self._get_plan_limit()
        self.rate_limit_minutes = rate_limit_minutes
        self.daily_usage = 0
        self.last_reset = datetime.utcnow()

    def _generate_api_key(self) -> str:
        return f"veh_{''.join(secrets.token_hex(16))}"

    def _get_plan_limit(self) -> int:
        plan_limits = {
            'free': 100,
            'basic': 1000,
            'premium': 10000
        }
        return plan_limits.get(self.plan, 100)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "api_key": self.api_key,
            "user_id": self.user_id,
            "name": self.name,
            "plan": self.plan,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "daily_limit": self.daily_limit,
            "daily_usage": self.daily_usage,
            "last_reset": self.last_reset
        }

    def _get_daily_limit(self) -> int:
        """Get daily request limit based on plan"""
        limits = {
            'free': 1000,  # 1000 requests per day
            'basic': 5000,  # 5000 requests per day
            'premium': 20000,  # 20000 requests per day
            'enterprise': 100000  # 100000 requests per day
        }
        return limits.get(self.plan, 1000)

    def _get_rate_limit(self) -> dict:
        """Get rate limit configuration based on plan"""
        return {
            'free': {'requests': 100, 'per_seconds': 60},  # 100 requests per minute
            'basic': {'requests': 200, 'per_seconds': 60},  # 200 requests per minute
            'premium': {'requests': 600, 'per_seconds': 60},  # 600 requests per minute
            'enterprise': {'requests': 1, 'per_seconds': 1}  # 1 request per second (unlimited)
        }.get(self.plan, {'requests': 100, 'per_seconds': 60})
