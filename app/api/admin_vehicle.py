from flask_restful import Resource
import logging
from flask import request, jsonify, make_response
from flask_pymongo import ObjectId

from app.enums.roles import Roles
from app.schemas.vehicles import vehicle_entity
from app.utils.validity_checks import is_valid_object_id
from app.utils.token_req import tokenReq
from app.utils.get_userid_token import get_userid_token


class AdminVehicleResource(Resource):
    """
    A class representing a RESTful API resource for managing route and team assignment.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the AdminVehicleResource class.
        Args:
            **kwargs: Keyword arguments that contain a reference to the vehicle collection.
        Returns:
            None
        """
        self.vehicle_collection = kwargs["vehicle"]
        self.route_collection = kwargs['route']
        self.user_collection = kwargs["user"]

    @tokenReq(Roles.ADMIN.value)
    def put(self):
        status = 'fail'
        code = 500
        data = {}
        message = ''
        try:
            user_id = get_userid_token()
            payload = request.get_json()
            vehicle_id = request.args.get("vehicle")

            if vehicle_id and is_valid_object_id(vehicle_id):
                existing_vehicle = self.vehicle_collection.find_one({'_id': ObjectId(vehicle_id)})
                if existing_vehicle:
                    update_payload = {}
                    if "current_route" in payload and payload["current_route"]\
                            and is_valid_object_id(payload["current_route"]):
                        existing_route = self.route_collection.find_one({"_id": ObjectId(payload["current_route"])})
                        if existing_route:
                            update_payload.update({"current_route": payload["current_route"]})
                            logging.info(f"ADMIN {user_id} send request with route id that to update {vehicle_id}")
                        else:
                            message = 'Route not found'
                            code = 404
                            logging.warning(f"ADMIN {user_id} send request with route id that does not exist")
                    else:
                        message = 'Invalid route id.'
                        code = 400
                        logging.warning(f"ADMIN {user_id} send request without route id")

                    if "current_team" in payload:
                        if payload["current_team"] and is_valid_object_id(payload["current_team"]):
                            existing_manager = self.user_collection.find_one({"_id": ObjectId(payload["current_team"])})
                            if existing_manager:
                                update_payload.update({"current_team": payload["current_team"]})
                                logging.info(f"ADMIN {user_id} send request to assign different user from vehicle")
                            else:
                                message = 'Manager not found'
                                code = 404
                                logging.warning(f"ADMIN {user_id} send request with user that does not exist")
                        elif payload["current_team"] == '':
                            update_payload.update({"current_team": payload["current_team"]})
                            logging.warning(f"ADMIN {user_id} send request to unassign user from vehicle")
                        else:
                            message = "Invalid current team"
                            code = 400
                            logging.warning(f"ADMIN {user_id} send request with invalid team user id")
                    else:
                        message = 'Current team not provided'
                        code = 400
                        logging.warning(f"ADMIN {user_id} send request without team user id")

                    if len(update_payload) > 0:
                        req_payload = vehicle_entity(update_payload)
                        result_doc = self.vehicle_collection.update_one({"_id": ObjectId(vehicle_id)},
                                                                        {"$set": req_payload})

                        if result_doc.matched_count == result_doc.modified_count:
                            message = 'Successfully updated the vehicle'
                            code = 200
                            status = 'success'
                            data = vehicle_entity(self.vehicle_collection.find_one({'_id': vehicle_id}))
                            logging.info(f"ADMIN {user_id} updated vehicle {vehicle_id} successfully")
                        else:
                            message = 'Vehicle details were not updated.'
                            code = 200
                            status = 'success'
                            data = vehicle_entity(existing_vehicle)
                            logging.info(f"ADMIN {user_id} updated vehicle {vehicle_id} with existing details")
                else:
                    message = 'Vehicle not found'
                    code = 404
                    logging.warning(f"ADMIN {user_id} send request for vehicle that does not exist")
            else:
                message = 'Bad request'
                code = 400
                logging.warning(f"ADMIN {user_id} send request for vehicle with invalid id")
        except Exception as ex:
            message = f"{ex}"
            logging.debug(f"ADMIN {user_id} send request to unassign user from vehicle")

        return make_response(jsonify({'message': message, "status": status, "data": data}), code)
