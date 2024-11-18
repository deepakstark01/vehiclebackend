# Desc: Service to get vehicle details from vehicle number
from src.services.vehicledata import get_vehicle_details, getChallan
def get_vehicle_details_from_number(vehNum):
    number = vehNum.upper()
    header_element, challans = getChallan(number)
    data = ""
    onwer_name = ""
    # Prepare the response data

    if get_vehicle_details(vehNum) != "no":
        vdata = get_vehicle_details(vehNum)
        onwer_name = vdata['user']['name']
        data = vdata['vehicle']
    response_data = {
        'vehNum': number,
        'onwer_name': onwer_name,
        'header_element': header_element,
        'challans': challans,
        'vehicleDetails': data
    }
    return response_data