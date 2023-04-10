from bson.objectid import ObjectId
import re


def is_valid_email(email):
    """
    This function checks if provided email is valid.
    Args:
        email (str): String representing an email address.
    Returns:
        Boolean indicating whether the provided email is valid.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_input_value(input_value):
    pattern = r'^[a-zA-Z0-9\s.-]*$'
    return bool(re.match(pattern, input_value))


def is_valid_object_id(o_id):
    try:
        ObjectId(o_id)
        return True;
    except Exception:
        return False


def is_vehicle_plate_valid(vehicle_number):
    regex = r"(^[A-Z]{2}[0-9]{2} [A-Z]{3}$)|(^[A-Z][0-9]{1,3} [A-Z]{3}$)|(^[A-Z]{3} [0-9]{1,3}[A-Z]$)" \
            r"|(^[0-9]{1,4} [A-Z]{1,2}$)|(^[0-9]{1,3} [A-Z]{1,3}$)|(^[A-Z]{1,2} [0-9]{1,4}$)|(^[A-Z]{1,3} [0-9]{1,3}$)"
    return bool(re.match(regex, vehicle_number))
