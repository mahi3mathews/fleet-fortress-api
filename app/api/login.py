from flask_restful import Resource
import jwt
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask import request, jsonify, make_response
import logging

from app.schemas.users import user_entity
from app.utils.validity_checks import is_valid_email

bcrypt = Bcrypt()

failed_attempts = {}
lockout_time = 60 * 30


def handle_invalid_login(email):
    print(email)
    print(failed_attempts, "FAILED")
    if email in failed_attempts:
        failed_attempts[email]['count'] += 1
        failed_attempts[email]['timestamp'] = datetime.now()
    else:
        failed_attempts[email] = {'count': 1, 'timestamp': datetime.now()}


def check_user_failed_attempt(email):
    print(email, failed_attempts)
    if email in failed_attempts and failed_attempts[email]['count'] >= 3:
        time_elapsed = datetime.now() - failed_attempts[email]['timestamp']
        time_left = timedelta(seconds=lockout_time) - time_elapsed
        minutes, seconds = divmod(time_left.seconds, 60)
        formatted_time_left = f"{minutes:02d}:{seconds:02d}"
        return True, formatted_time_left
    else:
        return False, None


class LoginResource(Resource):
    def __init__(self, **kwargs):
        self.user_collection = kwargs["user"]
        self.secret_key = kwargs["secret_key"]

    def post(self):
        """
          This function handles user authentication by verifying the user's email and password.
          It expects a POST request with JSON payload containing the user's email and password.
          If the email and password are correct, it returns a JSON response with a status code of 200 and
          an authentication token along with the user's data (except for the password). If the email or password
          is incorrect, it returns a JSON response with an appropriate error message and a status code of 401.
          Args:
              None.
          Returns:
              A JSON response containing the following keys:
                  - status (str): A string indicating the status of the authentication request.
                  - data (dict): A dictionary containing the authentication token and the user's data (except for the password).
                  - message (str): A string containing a message describing the status of the authentication request.
        """
        res_data = {}

        try:
            request_payload = request.get_json()

            if "email" in request_payload and is_valid_email(request_payload["email"]):
                email = request_payload['email']
                user = self.user_collection.find_one({"email": request_payload["email"]})
                print(user)
                invalid_attempt, lockout_time_user = check_user_failed_attempt(email)
                print(invalid_attempt)
                if invalid_attempt:
                    message = f'Account locked out. Please try again in {lockout_time_user} seconds.'
                    status = 'fail'
                    code = 401
                    logging.warning(f"User {email} is locked out from logging in.")
                else:
                    if user:
                        user["_id"] = str(user["_id"])
                        if user and bcrypt.check_password_hash(user['password'], request_payload['password']):
                            time = datetime.utcnow() + timedelta(hours=5)
                            token = jwt.encode({
                                "user": {
                                    "email": f"{user['email']}",
                                    "id": f"{user['_id']}",
                                    "role": f"{user['role']}"
                                },
                                "exp": time
                            }, self.secret_key)
                            del user['password']
                            message = f"User Authenticated"
                            code = 200
                            status = "successful"
                            res_data['user'] = user_entity(user)
                            if email in failed_attempts:
                                del failed_attempts[email]
                            logging.info(f"User {email} successfully logged in")
                        else:
                            handle_invalid_login(email)
                            message = "Invalid credentials."
                            code = 401
                            status = "fail"
                            logging.warning(f"User {email} send login request with incorrect credentials")
                    else:
                        handle_invalid_login(email)
                        message = "Invalid credentials."
                        code = 401
                        status = "fail"
                        logging.warning(f"User {email} send login request with incorrect credentials")
            else:
                message = 'Invalid credentials provided.'
                code = 400
                logging.warning(f"User send login request with invalid credentials")

        except Exception as ex:
            print(ex)
            message = f"{ex}"
            code = 500
            status = 'fail'
            logging.debug(f"User login exception {ex}")

        response_entity = make_response(jsonify({"status": status, "data": res_data, "message": message}), code)
        if code == 200:
            response_entity.headers["Authorization"] = f'Bearer {token}'
            response_entity.set_cookie(key='jwt_token', value=token, expires=time, httponly=True)

        return response_entity
