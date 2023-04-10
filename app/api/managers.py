from flask_restful import Resource
from flask import jsonify, make_response
import logging

from app.utils.token_req import tokenReq
from app.schemas.managers import manager_list_entity
from app.schemas.vehicles import vehicle_entity
from app.enums.roles import Roles
from app.enums.vehicle_route_status import VehicleRouteStatus
from app.utils.get_userid_token import get_userid_token


class ManagerResource(Resource):

    def __init__(self, **kwargs):
        self.user_collection = kwargs["user"]
        self.vehicle_collection = kwargs["vehicle"]

    @tokenReq(Roles.ADMIN.value)
    def get(self):
        status = 'fail'
        code = 500
        data = {}
        user_id = get_userid_token()
        try:
            existing_managers = list(self.user_collection.find({"role": Roles.MANAGER.value}))
            manager_ids = [str(manager["_id"]) for manager in existing_managers]
            all_manager_vehicles = list(self.vehicle_collection.find({"current_team": {"$in": manager_ids}}))
            manager_with_vehicle_list = []
            for manager in existing_managers:
                manager_info = manager
                assigned_vehicles = []
                for vehicle in all_manager_vehicles:
                    if vehicle["current_team"] == str(manager["_id"]):
                        assigned_vehicles.append(vehicle_entity(vehicle))
                        if vehicle["status"] != VehicleRouteStatus.NOT_STARTED.name:
                            manager_info.update({"current_route": vehicle["current_route"],
                                                 "route_status": vehicle["status"], 'vehicle': str(vehicle["_id"])})

                manager_info.update({"assigned_vehicles": assigned_vehicles})
                manager_with_vehicle_list.append(manager_info)
            data = manager_list_entity(manager_with_vehicle_list)
            message = 'Successfully fetched all managers.'
            code = 200
            status = 'success'
            logging.info(f"ADMIN {user_id} fetched all managers in system")
        except Exception as ex:
            message = f"{ex}"
            logging.info(f"ADMIN {user_id} tried to fetch all managers and failed {ex}")

        return make_response(jsonify({"message": message, "status": status, "data": data}), code)
