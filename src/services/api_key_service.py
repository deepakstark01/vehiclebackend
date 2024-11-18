# src/services/api_key_service.py
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Tuple, Optional
from bson import ObjectId
from ..models.api_key import APIKey


class APIKeyService:
    def __init__(self, db):
        self.db = db
        self.url_key_collection = db.url_key
        self.api_keys_collection = db.api_keys
        self.logger = logging.getLogger(__name__)

    def create_api_key(self, user_id: str, name: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """Create new API key for user based on their plan"""
        try:
            # Get user's plan
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None, "User not found"

            # Check if user's plan is active
            if user.get('plan_expiry') and datetime.utcnow() > user['plan_expiry']:
                return None, "Subscription plan has expired"

            # Check existing keys count and limit based on plan
            plan_limits = {
                'free': 100,
                'basic': 500,
                'premium': 1000,
                'enterprise': 2000
            }
            max_keys = plan_limits.get(user['plan'], 100)  # Default to free plan limit

            existing_keys = self.api_keys_collection.count_documents({
                "user_id": user_id,
                "is_active": True
            })

            if existing_keys >= max_keys:
                return None, f"Maximum API keys limit reached ({max_keys}) for your plan"

            # Get plan configurations
            plan_configs = {
                'free': {'daily_limit': 100, 'rate_limit_minutes': 1},
                'basic': {'daily_limit': 1000, 'rate_limit_minutes': 0.5},
                'premium': {'daily_limit': 10000, 'rate_limit_minutes': 0.1},
                'enterprise': {'daily_limit': 100000, 'rate_limit_minutes': 0}
            }

            plan_config = plan_configs.get(user['plan'])

            # Create API key with user's plan settings
            api_key = APIKey(
                user_id=user_id,
                name=name,
                rate_limit_minutes=plan_config['rate_limit_minutes'],
                plan=user['plan']
            )

            key_data = api_key.to_dict()
            result = self.api_keys_collection.insert_one(key_data)
            key_data['_id'] = str(result.inserted_id)

            return key_data, None

        except Exception as e:
            self.logger.error(f"Error creating API key: {str(e)}")
            return None, str(e)

    # def check_rate_limit(self, key_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    #     """
    #     Check if request is within rate limits
    #     Returns: (is_allowed, error_message)
    #     """
    #     try:
    #         current_time = datetime.utcnow()
    #
    #         # Get rate limit configuration
    #         rate_limits = {
    #             'free': {'requests': 100, 'window': 60},  # 100 per minute
    #             'basic': {'requests': 200, 'window': 60},  # 200 per minute
    #             'premium': {'requests': 600, 'window': 60},  # 600 per minute
    #             'enterprise': {'requests': 1, 'window': 1}  # 1 per second
    #         }
    #
    #         plan = key_data.get('plan', 'free')
    #         print(plan)
    #         limit_config = rate_limits.get(plan, rate_limits['free'])
    #
    #         # Check if we need to reset the counter
    #         last_reset = key_data.get('last_reset', datetime.min)
    #         time_diff = (current_time - last_reset).total_seconds()
    #
    #         if time_diff >= limit_config['window']:
    #             # Reset counter if window has passed
    #             self.api_keys_collection.update_one(
    #                 {"_id": key_data['_id']},
    #                 {
    #                     "$set": {
    #                         "requests_count": 1,
    #                         "last_reset": current_time,
    #                         "last_used": current_time
    #                     }
    #                 }
    #             )
    #             return True, None
    #         # Check if within rate limit
    #         if key_data.get('requests_count', 0) >= limit_config['requests']:
    #             wait_time = limit_config['window'] - time_diff
    #             return False, f"Rate limit exceeded. Please wait {int(wait_time)} seconds."
    #
    #         # Increment request counter
    #         self.api_keys_collection.update_one(
    #             {"_id": key_data['_id']},
    #             {
    #                 "$inc": {"requests_count": 1},
    #                 "$set": {"last_used": current_time}
    #             }
    #         )
    #
    #         return True, None
    #
    #     except Exception as e:
    #         self.logger.error(f"Error checking rate limit: {str(e)}")
    #         return True, None  # Allow request on error
    #

    def check_rate_limit(self, key_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Check both rate limits and daily usage limits
        Returns: (is_allowed, error_message)
        """
        try:
            current_time = datetime.utcnow()

            # First, check daily usage
            daily_limits = {
                'free': 1000,  # 1000 requests per day
                'basic': 5000,  # 5000 requests per day
                'premium': 20000,  # 20000 requests per day
                'enterprise': 100000  # 100000 requests per day
            }

            plan = key_data.get('plan', 'free')
            daily_limit = daily_limits.get(plan, daily_limits['free'])

            # Check if we need to reset daily usage
            last_reset_daily = key_data.get('last_daily_reset')
            if last_reset_daily:
                if isinstance(last_reset_daily, str):
                    last_reset_daily = datetime.fromisoformat(last_reset_daily.replace('Z', '+00:00'))

                days_passed = (current_time - last_reset_daily).days

                if days_passed >= 1:
                    # Reset daily usage
                    self.api_keys_collection.update_one(
                        {"_id": key_data['_id']},
                        {
                            "$set": {
                                "daily_usage": 1,
                                "last_daily_reset": current_time
                            }
                        }
                    )
                else:
                    # Check daily limit
                    daily_usage = key_data.get('daily_usage', 0)
                    if daily_usage >= daily_limit:
                        next_reset = last_reset_daily + timedelta(days=1)
                        wait_hours = (next_reset - current_time).total_seconds() / 3600
                        return False, f"Daily limit exceeded. Resets in {int(wait_hours)} hours"

            else:
                # Initialize daily tracking
                self.api_keys_collection.update_one(
                    {"_id": key_data['_id']},
                    {
                        "$set": {
                            "daily_usage": 1,
                            "last_daily_reset": current_time
                        }
                    }
                )

            # Now check rate limits (per minute/second)
            rate_limits = {
                'free': {'requests': 100, 'window': 60},  # 100 per minute
                'basic': {'requests': 200, 'window': 60},  # 200 per minute
                'premium': {'requests': 600, 'window': 60},  # 600 per minute
                'enterprise': {'requests': 1, 'window': 1}  # 1 per second
            }

            limit_config = rate_limits.get(plan, rate_limits['free'])

            # Check rate limit window
            last_reset = key_data.get('last_reset')
            if not last_reset:
                # First request, initialize the window
                self.api_keys_collection.update_one(
                    {"_id": key_data['_id']},
                    {
                        "$set": {
                            "requests_count": 1,
                            "last_reset": current_time,
                            "last_used": current_time
                        },
                        "$inc": {"daily_usage": 1}
                    }
                )
                return True, None

            if isinstance(last_reset, str):
                last_reset = datetime.fromisoformat(last_reset.replace('Z', '+00:00'))

            time_diff = (current_time - last_reset).total_seconds()

            # Check if we need to reset the rate limit window
            if time_diff >= limit_config['window']:
                # Start new window
                self.api_keys_collection.update_one(
                    {"_id": key_data['_id']},
                    {
                        "$set": {
                            "requests_count": 1,
                            "last_reset": current_time,
                            "last_used": current_time
                        },
                        "$inc": {"daily_usage": 1}
                    }
                )
                return True, None

            # Check rate limit
            current_count = key_data.get('requests_count', 0)
            if current_count >= limit_config['requests']:
                wait_time = limit_config['window'] - time_diff
                return False, (
                    f"Rate limit exceeded. "
                    f"Limit is {limit_config['requests']} requests per "
                    f"{limit_config['window']} seconds. "
                    f"Please wait {int(wait_time)} seconds."
                )

            # Update counters
            self.api_keys_collection.update_one(
                {"_id": key_data['_id']},
                {
                    "$inc": {
                        "requests_count": 1,
                        "daily_usage": 1
                    },
                    "$set": {"last_used": current_time}
                }
            )

            # Add debug logging
            self.logger.debug(
                f"Usage check - Plan: {plan}, "
                f"Rate: {current_count + 1}/{limit_config['requests']}, "
                f"Daily: {key_data.get('daily_usage', 0) + 1}/{daily_limit}"
            )

            return True, None

        except Exception as e:
            self.logger.error(f"Error checking usage limits: {str(e)}", exc_info=True)
            return True, None  # Allow request on error



    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Validate API key and check usage limits"""
        try:
            key_data = self.api_keys_collection.find_one({"api_key": api_key})

            if not key_data:
                return False, None, "Invalid API key"

            if not key_data['is_active']:
                return False, None, "API key is inactive"

            # Reset daily usage if needed
            if (datetime.utcnow() - key_data['last_reset']).days > 0:
                self.api_keys_collection.update_one(
                    {"api_key": api_key},
                    {
                        "$set": {
                            "daily_usage": 0,
                            "last_reset": datetime.utcnow()
                        }
                    }
                )
                key_data['daily_usage'] = 0

            # Check daily limit
            if key_data['daily_usage'] >= key_data['daily_limit']:
                return False, key_data, "Daily API limit exceeded"

            # Check rate limit


            # Update usage
            self.api_keys_collection.update_one(
                {"api_key": api_key},
                {
                    "$inc": {"daily_usage": 1},
                    "$set": {"last_used": datetime.utcnow()}
                }
            )

            return True, key_data, None

        except Exception as e:
            self.logger.error(f"Error validating API key: {str(e)}")
            return False, None, str(e)

    def get_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        try:
            keys = list(self.api_keys_collection.find({"user_id": user_id}))
            for key in keys:
                key['_id'] = str(key['_id'])
            return keys
        except Exception as e:
            self.logger.error(f"Error fetching API keys: {str(e)}")
            return []

    def revoke_api_key(self, user_id: str, api_key: str) -> Tuple[bool, Optional[str]]:
        """Revoke an API key"""
        try:
            result = self.api_keys_collection.update_one(
                {"user_id": user_id, "api_key": api_key},
                {"$set": {"is_active": False}}
            )
            if result.modified_count:
                return True, None
            return False, "API key not found"
        except Exception as e:
            self.logger.error(f"Error revoking API key: {str(e)}")
            return False, str(e)
    def get_url_key(self):
        return self.url_key_collection.find_one({"url_data": "url_key"})['value']