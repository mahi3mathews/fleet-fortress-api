from flask_pymongo import ObjectId


def manager_entity(manager_info):
    formatted_entity = {
        "id": str(ObjectId(manager_info["_id"])),
        "name": manager_info["name"],
        "email": manager_info["email"],
        "created_on": manager_info["created_on"]
    }
    if "assigned_vehicles" in manager_info:
        formatted_entity.update({"assigned_vehicles": manager_info["assigned_vehicles"]})
    if 'current_route' in manager_info:
        formatted_entity.update({"current_route": manager_info["current_route"]})
    if "current_vehicle" in manager_info:
        formatted_entity.update({"current_vehicle": manager_info["current_vehicle"]})
    return formatted_entity


def manager_list_entity(manager_list):
    formatted_list = []
    for manager in manager_list:
        formatted_list.append(manager_entity(manager))
    return formatted_list
