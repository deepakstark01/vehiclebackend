# src/middlewares/role_check.py
from functools import wraps
from flask import jsonify
from typing import Callable

def admin_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') not in ['admin', 'superadmin']:
            return jsonify({
                'status': 'error',
                'message': 'Admin privileges required'
            }), 403

        return f(current_user, *args, **kwargs)
    return decorated