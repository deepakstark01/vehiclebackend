
from datetime import datetime, timedelta
from typing import Dict, Set
import time

class SecurityManager:
    def __init__(self):
        self.nonces: Set[str] = set()
        self.nonce_expiry = 300  # 5 minutes
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()

    def cleanup_nonces(self):
        """Clean up expired nonces periodically"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self.nonces.clear()
            self.last_cleanup = current_time

    def verify_nonce(self, nonce: str) -> bool:
        """Verify nonce hasn't been used"""
        self.cleanup_nonces()
        if nonce in self.nonces:
            return False
        self.nonces.add(nonce)
        return True
