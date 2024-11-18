# src/routes/vehicle_routes.py
from flask import Blueprint, request, jsonify
from src.controllers.vehicle_controller import VehicleController
from src.middlewares.auth import token_required

bp = Blueprint('vehicles', __name__)
vehicle_controller = VehicleController()


@bp.route('/data', methods=['POST'])
@token_required
def get_vehicle(current_user):
    """Get vehicle details from POST body"""
    try:
        data = request.get_json()

        if not data or 'veh_num' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Vehicle number is required in request body'
            }), 400

        veh_num = data['veh_num']
        return vehicle_controller.get_vehicle_details(veh_num)

    except Exception as e:

        return jsonify({
            'status': 'error',
            'message': f'Invalid request: {str(e)}'
        }), 400