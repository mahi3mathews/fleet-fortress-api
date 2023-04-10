from flask_restful import Resource
from app.utils.token_req import tokenReq
from flask import request, jsonify, make_response
from flask_pymongo import ObjectId
from datetime import datetime
import logging

from app.enums.roles import Roles
from app.enums.record_count import RecordCount
from app.enums.vehicle_route_status import VehicleRouteStatus
from app.schemas.vehicles import vehicle_entity, vehicle_list_entity, create_vehicle_entity
from app.schemas.users import user_entity
from app.utils.validity_checks import is_vehicle_plate_valid, is_valid_object_id
from app.utils.get_userid_token import get_userid_token


def check_vehicle_validity(payload):
    if "vehicle_number" not in payload:
        return False
    elif not payload["vehicle_number"] or is_vehicle_plate_valid(payload["vehicle_number"]):
        return False
    else:
        return True


class VehicleResource(Resource):
    """
    A class representing a RESTful API resource for managing vehicles.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the VehicleResource class.
        Args:
            **kwargs: Keyword arguments that contain a reference to the vehicle collection.
        Returns:
            None
        """
        self.vehicle_collection = kwargs["vehicle"]
        self.user_collection = kwargs['user']
        self.route_collection = kwargs["route"]

    @tokenReq('')
    def get(self):
        """
        Retrieves a vehicle by its ID or all vehicles in the collection.
        Args:
            id: The ID of the vehicle to retrieve.
        Returns:
            A JSON response containing information about the retrieved vehicle(s).
        """
        status = 'fail'
        code = 500
        data = {}
        user_id = get_userid_token()
        try:
            vehicle_id = request.args.get("vehicle")
            if vehicle_id:
                if is_valid_object_id(vehicle_id):
                    found_vehicle = self.vehicle_collection.find_one({"_id": ObjectId(id)})
                    if found_vehicle:
                        data = vehicle_entity(found_vehicle)
                        message = 'Successfully fetched vehicle.'
                        status = 'success'
                        code = 200
                        logging.info(f"User {user_id} successfully fetched the vehicle {vehicle_id}")
                    else:
                        code = 404
                        message = 'Vehicle not found'
                        logging.warning(f"User {user_id} requested vehicle that does not exist")
                else:
                    message = 'Invalid vehicle id'
                    code = 400
                    logging.warning(f"User {user_id} provided invalid vehicle id")
            else:
                page_number = int(request.args.get("page"))
                if not page_number:
                    page_number = 1
                record_count = RecordCount.VEHICLE.value
                vehicle_query = {}
                if user_id:
                    user = self.user_collection.find_one({"_id": ObjectId(user_id)})
                    if not user:
                        message = 'User not found'
                        code = 401
                        logging.warning(f"User {user_id} is not found to access the vehicles list")
                    else:
                        if user["role"] == Roles.MANAGER.value:
                            vehicle_query.update({"current_team": {"$in": [user_id, '']}})
                        vehicle_list = list(self.vehicle_collection.find(vehicle_query).sort("name").
                                            skip(record_count * (page_number - 1)).limit(record_count))
                        total_vehicle_records = self.vehicle_collection.count_documents(vehicle_query)
                        vehicle_final_list = []
                        for vehicle in vehicle_list:
                            vehicle_data = vehicle
                            if vehicle["current_route"]:
                                route_info = self.route_collection.find_one({"_id": ObjectId(vehicle["current_route"])})
                                vehicle_data.update({"route_info": route_info})
                            if vehicle["current_team"]:
                                manager_info = self.user_collection.find_one({"_id": ObjectId(vehicle["current_team"])})
                                vehicle_data.update({"manager_info": manager_info})
                            vehicle_final_list.append(vehicle_data)

                        message = 'Successfully fetched all vehicles.'
                        data = {"vehicles": vehicle_list_entity(vehicle_final_list),
                                'total_records': total_vehicle_records}
                        status = 'success'
                        code = 200
                        logging.info(f"User {user_id} successfully fetched the vehicles list")
                else:
                    message = 'Unauthorized'
                    code = 401
                    logging.warning(f"Unauthorized attempt to access vehicles")

        except Exception as ex:
            message = f"{ex}"
            logging.warning(f"User failed to fetch vehicles due to {ex}")
        return make_response(jsonify({"message": message, 'data': data, "status": status}), code)

    @tokenReq(Roles.ADMIN.value)
    def post(self):
        """
        Creates a new vehicle in the collection.
        Returns:
            A JSON response containing information about the created vehicle.
        """
        status = 'fail'
        code = 500
        data = {}
        user_id = get_userid_token()
        try:
            payload = request.get_json()
            if check_vehicle_validity(payload):
                code = 400
                message = 'Incorrect/Invalid vehicle request'
                logging.warning(f"User {user_id} provided incorrect vehicle number")
            else:
                vehicle_exist = self.vehicle_collection.find_one({"vehicle_number": payload['vehicle_number']})
                if vehicle_exist:
                    message = 'Vehicle already exists.'
                    code = 409
                    logging.warning(f"User {user_id} tried to create vehicle with existing vehicle number")
                else:
                    payload["current_route"] = ''
                    payload["status"] = VehicleRouteStatus.NOT_STARTED.name
                    payload["current_team"] = ""
                    payload["former_teams"] = []
                    payload["created_on"] = datetime.now()
                    payload["former_routes"] = []
                    vehicle_created = self.vehicle_collection.insert_one(create_vehicle_entity(payload))
                    data = {"id": str(ObjectId(vehicle_created.inserted_id))}
                    message = f"Successfully created vehicle {payload['vehicle_number']}"
                    code = 200
                    status = 'success'
                    logging.info(f"User {user_id} created vehicle {str(vehicle_created.inserted_id)}")
        except Exception as ex:
            message = f"{ex}"
            logging.debug(f"User {user_id} failed to create vehicle due to {ex}")
        return make_response(jsonify({"data": data, "message": message, "status": status}), code)

    @tokenReq(Roles.ADMIN.value)
    def delete(self):
        status = 'fail'
        code = 500
        user_id = get_userid_token()
        try:
            vehicle_id = request.args.get("vehicle")
            if vehicle_id and is_valid_object_id(vehicle_id):
                existing_vehicle = self.vehicle_collection.find_one({"_id": ObjectId(vehicle_id)})
                if existing_vehicle:
                    if existing_vehicle["status"] != VehicleRouteStatus.NOT_STARTED.name and \
                            existing_vehicle['status'] != VehicleRouteStatus.ON_DESTINATION.name:
                        message = 'Vehicle is currently on route. Cannot remove vehicle.'
                        code = 400
                        logging.warning(f"User {user_id} tried to delete vehicle which is on route")
                    else:
                        deleted_doc = self.vehicle_collection.delete_one({"_id": ObjectId(vehicle_id)})
                        if deleted_doc.deleted_count == 1:
                            message = f'Successfully removed vehicle {existing_vehicle["name"]}'
                            status = 'success'
                            code = 200
                            logging.info(f"User {user_id} deleted vehicle {vehicle_id}")
                        else:
                            message = 'Failed to remove vehicle'
                            logging.warning(f"User {user_id} failed to delete vehicle")
                else:
                    message = 'Vehicle not found.'
                    code = 404
                    logging.warning(f"User {user_id} tried to delete vehicle that does not exist")
            else:
                message = 'Bad request'
                code = 400
                logging.warning(f"User {user_id} tried to delete vehicle with invalid id")
        except Exception as ex:
            message = f"{ex}"
            logging.warning(f"User {user_id} failed to delete vehicle due to {ex}")
        return make_response(jsonify({"message": message, "status": status}), code)
