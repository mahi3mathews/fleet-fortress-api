from flask_restful import Resource
from flask_bcrypt import Bcrypt
from flask import jsonify, make_response

bcrypt = Bcrypt()


class LogoutResource(Resource):
    def __init__(self, **kwargs):
        self.user_collection = []
        self.secret_key = ''

    def post(self):
        """
          This function handles removing authentication by unsetting the cookies and returning the response
          It expects a POST request.
          Args:
              None.
          Returns:
              A JSON response containing the following keys:
                  - status (str): A string indicating the status of the authentication request.
                  - message (str): A string containing a message describing the status of the authentication request.
        """
        try:
            response = make_response(jsonify({'message': 'Successfully logged out'}), 200)
            response.set_cookie(key='jwt_token', value='', expires=0, httponly=True)
            return response
        except Exception as ex:
            message = f"{ex}"
            code = 500
            status = 'fail'
            response_entity = make_response(jsonify({"status": status, "message": message}), code)
            return response_entity
