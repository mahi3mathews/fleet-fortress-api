from flask_restful import Resource
from flask import make_response, jsonify
from flask_pymongo import ObjectId
from flask_bcrypt import Bcrypt
import logging

from app.schemas.users import user_entity
from app.utils.get_userid_token import get_userid_token
from app.utils.token_req import tokenReq

bcrypt = Bcrypt()


class UserResource(Resource):

    def __init__(self, **kwargs):
        self.user_collection = kwargs["user"]
        self.register_code_collection = kwargs["register_codes"]

    @tokenReq("")
    def get(self):
        data = {}
        status = 'fail'
        try:
            user_id = get_userid_token()
            if user_id:
                user = self.user_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    data = user_entity(user)
                    message = 'Successfully fetch user details'
                    status = 'success'
                    code = 200
                    logging.info(f"User {user_id} fetched details successfully")
                else:
                    message = 'User not found'
                    code = 404
                    logging.warning(f"User {user_id} does not exist")
            else:
                message = 'Invalid user id'
                code = 400
                logging.warning(f"User {user_id} provided invalid id")
        except Exception as ex:
            message = f"{ex}"
            status = 'fail'
            code = 500
            logging.debug(f"User failed to fetch their details {ex}")

        return make_response(jsonify({"message": message, "status": status, "data": data}), code)
