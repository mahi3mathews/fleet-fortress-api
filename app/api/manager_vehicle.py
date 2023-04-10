from flask_restful import Resource
from app.utils.token_req import tokenReq
from flask import request, jsonify, make_response
from flask_pymongo import ObjectId
import logging

from app.enums.roles import Roles
from app.enums.vehicle_route_status import VehicleRouteStatus
from app.enums.vehicle_status_change import VehicleStatusChange
from app.schemas.vehicles import vehicle_entity
from app.utils.get_userid_token import get_userid_token
from app.utils.validity_checks import is_valid_object_id


def is_user_valid_to_update(user, req, existing_user):
    if existing_user == user or (existing_user == "" and req == user):
        return True
    else:
        return False


def is_vehicle_allowed_to_update_team(vehicle_status):
    if vehicle_status != VehicleRouteStatus.NOT_STARTED.name:
        return False
    else:
        return True


def is_vehicle_status_allowed_to_update(status, route, req_status):
    if not route:
        if status == VehicleRouteStatus.ON_DESTINATION.name and req_status == VehicleRouteStatus.NOT_STARTED.name:
            return True
    return False


class ManagerVehicleResource(Resource):
    """
    A class representing a RESTful API resource for managing vehicles status and team assignment.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the ManagerVehicleResource class.
        Args:
            **kwargs: Keyword arguments that contain a reference to the vehicle collection.
        Returns:
            None
        """
        self.vehicle_collection = kwargs["vehicle"]

    @tokenReq(Roles.MANAGER.value)
    def put(self):
        status = 'fail'
        code = 0
        data = {}
        user_id = get_userid_token()
        if user_id and is_valid_object_id(user_id):
            try:
                payload = request.get_json()
                vehicle_id = request.args.get("vehicle")
                req_current_team = ''
                req_status = ''
                if "current_team" in payload and is_valid_object_id(payload["current_team"]):
                    req_current_team = payload["current_team"]
                if "status" in payload:
                    req_status = payload["status"]
                if vehicle_id and is_valid_object_id(vehicle_id):
                    existing_vehicle = self.vehicle_collection.find_one({'_id': ObjectId(vehicle_id)})
                    if existing_vehicle:
                        update_payload = {}
                        # Check if current user is allowed to modify the details of vehicle
                        if is_user_valid_to_update(
                                user=user_id, req=req_current_team, existing_user=existing_vehicle["current_team"]):
                            if not is_vehicle_allowed_to_update_team(existing_vehicle["status"]):
                                message = 'Invalid attempt to change team.'
                                code = 401
                                logging.warning(f"MANAGER {user_id} tried to change team for vehicle on route")
                            else:
                                update_payload.update({"current_team": req_current_team})
                                logging.info(f"MANAGER {user_id} updated team for vehicle on route")

                            if req_status not in VehicleStatusChange.status_flow[existing_vehicle["status"]]:
                                message = 'Invalid status transition'
                                code = 400
                                logging.warning(f"MANAGER {user_id} tried to update status incorrectly")
                            elif not is_vehicle_status_allowed_to_update(
                                    status=existing_vehicle["status"], route=existing_vehicle["route"],
                                    req_status=req_status):
                                message = 'No route is assigned to vehicle'
                                code = 400
                                logging.warning(f"MANAGER {user_id} tried to update status of vehicle with no route")
                            else:
                                update_payload.update({"status_name": req_status})
                                if req_status == VehicleRouteStatus.ON_DESTINATION.name:
                                    existing_routes = existing_vehicle["former_routes"]
                                    existing_routes.append(existing_vehicle["current_route"])
                                    update_payload.update({"former_routes": existing_routes})
                                    update_payload.update({"current_route": ''})
                                    existing_managers = existing_vehicle["former_teams"]
                                    existing_managers.append(existing_vehicle["current_team"])
                                    update_payload.update({"former_teams": existing_managers})
                                logging.info(f"MANAGER {user_id} update status {req_status} of vehicle")

                            if len(update_payload) > 0 and code == 0:
                                req_payload = vehicle_entity(update_payload)
                                result_doc = self.vehicle_collection.update_one({"_id": ObjectId(vehicle_id)},
                                                                                {"$set": req_payload})
                                if result_doc.matched_count == result_doc.modified_count:
                                    message = 'Successfully updated the vehicle'
                                    code = 200
                                    status = 'success'
                                    data = vehicle_entity(
                                        self.vehicle_collection.find_one({'_id': ObjectId(vehicle_id)}))
                                    logging.info(f"MANAGER {user_id} update document of vehicle {vehicle_id}")
                                else:
                                    message = 'Vehicle details were not updated.'
                                    code = 200
                                    status = 'success'
                                    data = vehicle_entity(existing_vehicle)
                                    logging.info(f"MANAGER {user_id} updated document with existing values")

                        else:
                            message = 'Unauthorised attempt to update vehicle.'
                            code = 401
                            status = 'fail'
                            logging.warning(f"MANAGER {user_id} made unauthorised attempt to update vehicle")
                    else:
                        message = 'Vehicle not found'
                        code = 404
                        logging.warning(f"MANAGER {user_id} made request for vehicle that does not exist")
                else:
                    message = 'Bad request'
                    code = 400
                    logging.warning(f"MANAGER {user_id} made bad request to update vehicle")

            except Exception as ex:
                message = f"{ex}"
                code = 500
                logging.debug(f"MANAGER {user_id} made request and failed with error {ex}")
        else:
            message = 'Unauthorised attempt to update vehicle'
            code = 401
            logging.warning(f"MANAGER {user_id} made unauthorised request to update vehicle")

        return make_response(jsonify({'message': message, "status": status, "data": data}), code)
