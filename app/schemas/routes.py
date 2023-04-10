from flask_pymongo import ObjectId


def route_entity(route_info):
    formatted_entity = {
        "id": str(ObjectId(route_info["_id"])),
        "name": route_info["name"],
        "start_loc": route_info["start_loc"],
        "end_loc": route_info["end_loc"],
        "created_on": route_info["created_on"]
    }
    return formatted_entity


def create_route_entity(route_info):
    formatted_entity = {
        "name": route_info["name"],
        "start_loc": route_info["start_loc"],
        "end_loc": route_info["end_loc"],
        "created_on": route_info["created_on"]
    }
    return formatted_entity


def route_list_entity(route_list):
    formatted_list = []
    for route in route_list:
        formatted_list.append(route_entity(route))
    return formatted_list
