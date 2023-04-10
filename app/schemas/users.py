from flask_pymongo import ObjectId


def create_user_entity(user_data):
    user = {
        "name": user_data["name"],
        "email": user_data["email"],
        "role": user_data["role"],
        "created_on": user_data["created_on"]
    }
    if "password" in user_data:
        user.update({"password": user_data["password"]})
    return user


def user_entity(user_data):
    return {
        "id": str(ObjectId(user_data["_id"])),
        "name": user_data["name"],
        "email": user_data["email"],
        "role": user_data["role"],
        "created_on": user_data["created_on"]
    }

