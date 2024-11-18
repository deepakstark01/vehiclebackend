from flask import jsonify
from src.services.vehicle import get_vehicle_details_from_number


class VehicleController:
    # def get_vehicle_details(self, vehNum):
    #     if not vehNum:
    #         return jsonify({"error": "Please provide a vehicle number"}), 400
    #
    #     try:
    #         number = vehNum.upper()
    #         response_data = get_vehicle_details_from_number(number)
    #         return response_data, 200
    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500

    def get_vehicle_details(self, vehNum):
        try:
            number = vehNum.upper()
            response_data = get_vehicle_details_from_number(number)
            if response_data is None:
                return {"error": "Vehicle not found"}, 404
            return response_data
        except Exception as e:
            return {"error": str(e)}, 500
