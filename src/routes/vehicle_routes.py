# src/routes/vehicle_routes.py
from flask import Blueprint, request, jsonify, current_app
from src.controllers.vehicle_controller import VehicleController
from src.middlewares.auth import token_required
from datetime import datetime
from src.middlewares.api_key_auth import require_api_key
from src.middlewares.rate_limit import check_rate_limit
from src.utils.security import SecurityManager
import hmac
import hashlib

bp = Blueprint('vehicles', __name__)
vehicle_controller = VehicleController()
# security_manager = SecurityManager()


# def verify_request_signature(request_data: dict, timestamp: str, signature: str) -> bool:
#     """Verify the request signature"""
#     try:
#         secret_key = current_app.config['SECRET_KEY']
#
#         # Create message to sign
#         message = timestamp
#         for key in sorted(request_data.keys()):
#             message += str(request_data[key])
#
#         # Create signature
#         expected_signature = hmac.new(
#             secret_key.encode(),
#             message.encode(),
#             hashlib.sha256
#         ).hexdigest()
#
#         return hmac.compare_digest(expected_signature, signature)
#     except Exception as e:
#         current_app.logger.error(f"Signature verification failed: {str(e)}")
#         return False
#
#
# @bp.route('/data', methods=['POST'])
# @token_required
# def get_vehicle(current_user):
#     """Get vehicle details with security checks"""
#     try:
#         # 1. Validate request data
#         data = request.get_json()
#         if not data or 'veh_num' not in data:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Vehicle number is required'
#             }), 400
#
#         # 2. Get and validate headers
#         client_id = request.headers.get('X-Client-ID')
#         timestamp = request.headers.get('X-Timestamp')
#         signature = request.headers.get('X-Signature')
#         nonce = request.headers.get('X-Nonce')
#
#         if not all([client_id, timestamp, signature, nonce]):
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Missing required security headers'
#             }), 401
#
#         # 3. Verify client ID
#         valid_clients = current_app.config.get('VALID_CLIENT_IDS', [])
#         if client_id not in valid_clients:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Invalid client ID'
#             }), 401
#
#         # 4. Check timestamp
#         try:
#             request_time = datetime.fromtimestamp(float(timestamp))
#             time_diff = abs((datetime.utcnow() - request_time).total_seconds())
#             if time_diff > 300:  # 5 minutes
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'Request expired'
#                 }), 401
#         except ValueError:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Invalid timestamp'
#             }), 401
#
#         # 5. Verify signature
#         if not verify_request_signature(data, timestamp, signature):
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Invalid request signature'
#             }), 401
#
#         # 6. Check nonce
#         if not security_manager.verify_nonce(nonce):
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Nonce already used'
#             }), 401
#
#         # 7. Process request
#         result = vehicle_controller.get_vehicle_details(data['veh_num'])
#
#         return jsonify({
#             'status': 'success',
#             'data': result
#         }), 200
#
#     except Exception as e:
#         current_app.logger.error(f"Request failed: {str(e)}")
#         return jsonify({
#             'status': 'error',
#             'message': 'Request processing failed'
#         }), 400


@bp.route('/data', methods=['POST'])
# @token_required
def get_vehicle():
    """Get vehicle details from POST body"""
    try:
        data = request.get_json()

        if not data or 'veh_num' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Vehicle number is required in request body'
            }), 400

        veh_num = data['veh_num']
        return  vehicle_controller.get_vehicle_details(veh_num)

    except Exception as e:

        return jsonify({
            'status': 'error',
            'message': f'Invalid request: {str(e)}'
        }), 400


@bp.route('/api/lookup', methods=['POST'])
@check_rate_limit  # Single decorator that handles both API key and rate limiting
def get_vehicle_api(key_data):
    """Get vehicle details using API key"""
    try:
        data = request.get_json()
        if not data or 'veh_num' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Vehicle number is required'
            }), 400

        veh_num = data['veh_num']
        result = vehicle_controller.get_vehicle_details(veh_num)
        return jsonify({
            'status': 'success',
            'data': result,
            'rate_limit': {
                'plan': key_data['plan'],
                'requests_made': key_data.get('requests_count', 0),
                'daily_limit': key_data.get('daily_limit'),
                'daily_usage': key_data.get('daily_usage', 0)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid request: {str(e)}'
        }), 400
