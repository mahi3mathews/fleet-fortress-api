from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_pymongo import ObjectId
import logging

from app.utils.get_userid_token import get_userid_token
from app.utils.token_req import tokenReq
from app.utils.validity_checks import is_valid_input_value, is_valid_object_id
from app.enums.record_count import RecordCount
from datetime import datetime
from app.enums.roles import Roles
from app.schemas.routes import route_entity, route_list_entity, create_route_entity


def validate_route_values(data):
    is_valid = False
    try:
        if "name" in data and data["name"] and is_valid_input_value(data["name"]):
            is_valid = True
        if "start_loc" in data and data["name"] and is_valid_input_value(data["name"]):
            is_valid = True
        if "end_loc" in data and data["name"] and is_valid_input_value(data["name"]):
            is_valid = True
    except Exception:
        is_valid = False
    return is_valid


class RouteResource(Resource):
    def __init__(self, **kwargs):
        """
        Constructor method for the RouteResource class.
        Args:
            **kwargs: A dictionary containing keyword arguments. Expected key:
            - 'route': The MongoDB collection object for routes.
        """
        self.route_collection = kwargs["route"]
        self.user_collection = kwargs["user"]
        self.vehicle_collection = kwargs['vehicle']

    @tokenReq(Roles.ADMIN.value)
    def post(self):
        """
        Method for handling POST requests to create a new route.
        Returns:
            A JSON response indicating the status of the request, with data
            containing the ID of the newly created route.
        """
        status = 'fail'
        data = {}
        code = 500
        user_id = get_userid_token()
        try:
            payload = request.get_json("data")
            if validate_route_values(payload):
                message = 'Incorrect request'
                code = 400
                logging.warning(f"ADMIN {user_id} provided incorrect/invalid route details")
            else:
                payload["created_on"] = datetime.now()
                route_created = self.route_collection.insert_one(create_route_entity(payload))
                message = 'Successfully added a route'
                code = 200
                data = {"id": str(route_created.inserted_id)}
                status = 'success'
                logging.info(f"ADMIN {user_id} added a route {str(route_created.inserted_id)}")
        except Exception as ex:
            message = f'{ex}'
            logging.debug(f"ADMIN {user_id} failed to create route due to {ex}")
        return make_response(jsonify({'status': status, "data": data, "message": message}), code)

    @tokenReq('')
    def get(self):
        """
        Method for handling GET requests to retrieve a single route by ID or a list
        of all routes paginated.
        Args:
            None
        Returns:
            A JSON response indicating the status of the request, with data
            containing the retrieved route or a list of routes.
        """
        status = 'fail'
        data = None
        code = 500
        user_id = get_userid_token()
        try:
            route_id = request.args.get("route")
            if route_id and is_valid_object_id(route_id):
                found_route = self.route_collection.find_one({"_id": ObjectId(id)})
                if found_route:
                    message = 'Successfully fetched the route.'
                    code = 200
                    data = route_entity(found_route)
                    status = 'success'
                    logging.info(f"User {user_id} fetched the route {route_id}")
                else:
                    message = 'Route not found'
                    code = 404
                    logging.warning(f"USER {user_id} provided route id that does not exist")
            else:
                page_number = request.args.get("page")
                is_fetch_all = request.args.get("all")

                if not page_number:
                    page_number = 1
                else:
                    page_number = int(page_number)
                record_count = RecordCount.ROUTE.value
                if is_fetch_all:
                    found_routes = self.route_collection.find()
                else:
                    found_routes = self.route_collection.find().sort("name"). \
                        skip(record_count * (page_number - 1)).limit(record_count)
                count_routes = self.route_collection.count_documents({})

                data = {"routes": route_list_entity(found_routes), "total_records": count_routes}
                message = 'Successfully fetched all routes.'
                code = 200
                status = 'success'
                logging.info(f"User {user_id} fetched the routes")

        except Exception as ex:
            message = f"{ex}"
            logging.info(f"User {user_id} tried to fetch the routes and failed due to {ex}")
        return make_response(jsonify({'status': status, "data": data, "message": message}), code)

    @tokenReq(Roles.ADMIN.value)
    def delete(self):
        status = 'fail'
        code = 500
        user_id = get_userid_token()
        try:
            route_id = request.args.get("id")
            if route_id and is_valid_object_id(route_id):
                existing_route = self.route_collection.find_one({"_id": ObjectId(route_id)})
                ongoing_route_vehicles = list(self.vehicle_collection.find({"current_route": route_id}))
                if existing_route and len(ongoing_route_vehicles) > 0:
                    message = 'Cannot remove route. Vehicle is currently on this route.'
                    code = 400
                    logging.warning(f"ADMIN {user_id} tried to delete the route {route_id} that is on route")
                elif existing_route:
                    deleted_doc = self.route_collection.delete_one({"_id": ObjectId(route_id)})
                    if deleted_doc.deleted_count == 1:
                        message = f'Successfully removed route {existing_route["name"]}'
                        status = 'success'
                        code = 200
                        logging.info(f"ADMIN {user_id} deleted the route {route_id}")
                    else:
                        message = 'Failed to remove route'
                        logging.warning(f"ADMIN {user_id} failed to delete the route")
                else:
                    message = 'Route not found.'
                    code = 404
                    logging.warning(f"ADMIN {user_id} provided route id that does not exist")
            else:
                message = 'Bad request'
                code = 400
                logging.warning(f"ADMIN {user_id} provided invalid route id to delete")
        except Exception as ex:
            message = f"{ex}"
            logging.debug(f"ADMIN {user_id} tried to delete route {route_id} and failed {ex}")

        return make_response(jsonify({"message": message, "status": status}), code)
