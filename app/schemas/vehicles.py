from app.enums.vehicle_route_status import VehicleRouteStatus
from flask_pymongo import ObjectId


def vehicle_entity(vehicle_info):
    formatted_entity = {}
    if "_id" in vehicle_info:
        formatted_entity.update({"id": str(ObjectId(vehicle_info["_id"]))})
    if "vehicle_number" in vehicle_info:
        formatted_entity.update({"vehicle_number": vehicle_info["vehicle_number"]})
    if "current_team" in vehicle_info:
        formatted_entity.update({"current_team": vehicle_info["current_team"]})
    if "former_teams" in vehicle_info:
        formatted_entity.update({"former_teams": vehicle_info["former_teams"], })
    if "status" in vehicle_info:
        formatted_entity.update({"status": VehicleRouteStatus[vehicle_info["status"]].value})
    if "status_name" in vehicle_info:
        formatted_entity.update({"status": VehicleRouteStatus[vehicle_info["status_name"]].name})
    if "created_on" in vehicle_info:
        formatted_entity.update({"created_on": vehicle_info["created_on"]})
    if "current_route" in vehicle_info:
        formatted_entity.update({"current_route": vehicle_info["current_route"]})
    if "former_routes" in vehicle_info:
        formatted_entity.update({"former_routes": vehicle_info["former_routes"]})
    if "manager_info" in vehicle_info and "name" in vehicle_info["manager_info"]:
        formatted_entity.update({"current_team_name": vehicle_info["manager_info"]["name"]})
    if 'route_info' in vehicle_info and "name" in vehicle_info["route_info"]:
        formatted_entity.update({"current_route_name": vehicle_info["route_info"]["name"]})
    return formatted_entity


def create_vehicle_entity(vehicle_info):
    formatted_entity = {}
    if "vehicle_number" in vehicle_info:
        formatted_entity.update({"vehicle_number": vehicle_info["vehicle_number"]})
    if "current_team" in vehicle_info:
        formatted_entity.update({"current_team": vehicle_info["current_team"]})
    if "former_teams" in vehicle_info:
        formatted_entity.update({"former_teams": vehicle_info["former_teams"], })
    if "status" in vehicle_info:
        formatted_entity.update({"status": vehicle_info["status"]})
    if "created_on" in vehicle_info:
        formatted_entity.update({"created_on": vehicle_info["created_on"]})
    if "current_route" in vehicle_info:
        formatted_entity.update({"current_route": vehicle_info["current_route"]})
    if "former_routes" in vehicle_info:
        formatted_entity.update({"former_routes": vehicle_info["former_routes"]})
    return formatted_entity


def vehicle_list_entity(vehicle_list):
    formatted_list = []
    for vehicle in vehicle_list:
        formatted_list.append(vehicle_entity(vehicle))
    return formatted_list
