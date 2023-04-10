from pathlib import Path
import os
from dotenv import load_dotenv
from flask import Flask
from flask.helpers import send_from_directory
from flask_restful import Api
from flask_cors import CORS, cross_origin
import logging

from app.db import user_collection, register_codes, route_collection, vehicle_collection
from app.enums import roles
from app.utils.validity_checks import is_valid_email
from app.api.user import UserResource
from app.api.route import RouteResource
from app.api.vehicle import VehicleResource
from app.api.managers import ManagerResource
from app.api.user_register import UserRegisterResource
from app.api.login import LoginResource
from app.api.logout import LogoutResource
from app.api.manager_vehicle import ManagerVehicleResource
from app.api.admin_vehicle import AdminVehicleResource

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
api = Api(app, prefix='/api/v1')


secret_key = os.getenv("JWT_SECRET_KEY")
origin_url = os.getenv("REACT_APP_URL")


print(origin_url)

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://buqxp359th.execute-api.eu-central-1.amazonaws.com"}})



api.add_resource(UserResource, '/user', '/user/generate-token',
                 resource_class_kwargs={'user': user_collection, "register_codes": register_codes})
api.add_resource(ManagerResource, '/user/managers',
                 resource_class_kwargs={'user': user_collection, "vehicle": vehicle_collection})
api.add_resource(RouteResource, '/route', resource_class_kwargs={'route': route_collection, "user": user_collection,
                                                                 "vehicle": vehicle_collection})
api.add_resource(AdminVehicleResource, '/vehicle/admin',
                 resource_class_kwargs={"vehicle": vehicle_collection, "route": route_collection,
                                        "user": user_collection})
api.add_resource(ManagerVehicleResource, "/vehicle/manager", resource_class_kwargs={"vehicle": vehicle_collection})
api.add_resource(VehicleResource, '/vehicle',
                 resource_class_kwargs={'vehicle': vehicle_collection,
                                        "route": route_collection, "user": user_collection})
api.add_resource(UserRegisterResource, '/register', resource_class_kwargs={'user': user_collection,
                                                                           "register_codes": register_codes})
api.add_resource(LoginResource, '/login', resource_class_kwargs={'user': user_collection, 'secret_key': secret_key})
api.add_resource(LogoutResource, '/logout', resource_class_kwargs={'user': user_collection, 'secret_key': secret_key})

logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)


@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
