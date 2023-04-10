from flask_restful import Resource
from flask import jsonify, request, make_response
from flask_bcrypt import Bcrypt
from datetime import datetime
import logging

from app.enums.roles import Roles
from app.utils.validity_checks import is_valid_email, is_valid_input_value
from app.schemas.users import create_user_entity

bcrypt = Bcrypt()


class UserRegisterResource(Resource):
    def __init__(self, **kwargs):
        self.user_collection = kwargs["user"]
        self.register_codes_collection = kwargs["register_codes"]

    def post(self):
        """
            Create a new user with the provided data in the request body.
            If the request URL contains a query parameter `usertoken`,
            a verification is made against the user token in the database
            before the security manager is created.
            If 'usertoken' is not present a user with role ADMIN is created.
            This endpoint expects a JSON payload containing user details, including email, password, and role.
            Returns:
                A JSON response indicating the status of the request and any relevant message.
        """
        message = ""
        code = 500
        status = "fail"
        try:
            payload = request.get_json()
            user_existing = self.user_collection.find_one({"email": payload["email"]})
            if user_existing:
                message = 'User already exists.'
                code = 409
                logging.warning(f"User tried to register with existing email")
            else:
                token_arg = request.args.get("usertoken")
                if token_arg:
                    registered_code = self.register_codes_collection.find_one({"email": payload["email"]})
                    if not registered_code:
                        message = 'Provided email is not found.'
                        code = 401
                        logging.warning(f"Manager tried to register with incorrect email")
                    elif "name" not in payload:
                        message = 'Incomplete request. No name was provided.'
                        code = 400
                        logging.warning(f"Manager tried to register without name")
                    elif bcrypt.check_password_hash(registered_code["token"], token_arg):
                        payload['password'] = bcrypt.generate_password_hash(payload['password']).decode('utf-8')
                        payload['created_on'] = datetime.now()
                        if not is_valid_email(payload["email"]):
                            status = 'fail'
                            message = "Email is invalid."
                            code = 400
                            logging.warning("Manager tried to register with invalid email")
                        else:
                            payload["role"] = Roles.MANAGER.value
                            res = self.user_collection.insert_one(create_user_entity(payload))
                            self.register_codes_collection.delete_one({"email": payload["email"]})
                            if res.acknowledged:
                                status = "successful"
                                message = "Security Manager created successfully"
                                code = 201
                                logging.info("Manager successfully registered in system")
                    else:
                        code = 401
                        message = "User token is invalid."
                        logging.warning("Manager tried to register with invalid token")
                else:
                    payload['password'] = bcrypt.generate_password_hash(payload['password']).decode('utf-8')
                    payload['created_on'] = datetime.now()
                    if not is_valid_email(payload["email"]):
                        status = 'fail'
                        message = "Email is invalid."
                        code = 400
                        logging.warning("Admin tried to register with invalid email")
                    elif 'name' not in payload:
                        status = 'fail'
                        message = 'Incomplete request. No name was provided.'
                        code = 400
                        logging.warning("Admin tried to register without name")
                    elif not payload["name"] or is_valid_input_value(payload["name"]):
                        status = 'fail'
                        message = 'Invalid name provided'
                        code = 400
                        logging.warning("Admin tried to register with invalid name")
                    else:
                        payload["role"] = Roles.ADMIN.value
                        print(payload)
                        res = self.user_collection.insert_one(payload)
                        if res.acknowledged:
                            status = "successful"
                            message = "Administrator registered successfully"
                            code = 201
                            logging.info("Admin successfully registered in the system")
        except Exception as ex:
            message = f"{ex}"
            status = "fail"
            code = 500
            logging.debug(f"User could not register due to {ex}")
        return make_response(jsonify({'status': status, "message": message}), code)
