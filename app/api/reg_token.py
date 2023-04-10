from flask_restful import Resource
from flask import jsonify, request, make_response
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import logging
import secrets

from app.utils.validity_checks import is_valid_email
from app.utils.get_userid_token import get_userid_token

bcrypt = Bcrypt()


class RegisterTokenResource(Resource):
    def __init__(self, **kwargs):
        self.user_collection = kwargs["user"]
        self.register_codes_collection = kwargs["register_codes"]

    def post(self):
        """
            Create a new manger's register token with the provided data in the request body.
            Returns:
                A salt hashed token
        """
        message = ""
        code = 500
        status = "fail"
        data = {}
        try:
            user_id = get_userid_token()
            payload = request.get_json()
            if 'email' not in payload:
                message = 'No email was provided'
                code = 400
                logging.warning(f"Admin {user_id} sent empty email")
            else:
                email = payload["email"]
                if not email or not is_valid_email(email):
                    message = 'Invalid email provided'
                    code = 400
                    logging.warning(f"Admin {user_id} sent invalid email {email}")
                else:
                    existing_user = self.user_collection.find_one({"email": email})
                    if existing_user:
                        message = 'User already exists'
                        code = 409
                        logging.warning(f"Admin {user_id} sent request to generate token for existing user")
                    else:
                        secret_token = secrets.token_hex(10)
                        token = bcrypt.generate_password_hash(secret_token).decode('utf-8')
                        existing_token = self.register_codes_collection.find_one({"email": email})
                        expiry_time = datetime.now() + timedelta(hours=24)
                        if existing_token:
                            self.register_codes_collection.update_one({"email": email}, {"$set": {"token": token}})
                        else:
                            self.register_codes_collection.insert_one(
                                {"email": email, "token": token, "expires": expiry_time})

                        message = 'Successfully added a register token for manager'
                        code = 200
                        status = 'success'
                        data = {"token": secret_token}

        except Exception as ex:
            message = f"{ex}"
            status = "fail"
            code = 500
            logging.debug(f"Admin could not generate token due to {ex}")
        return make_response(jsonify({'status': status, "message": message, "data": data}), code)
