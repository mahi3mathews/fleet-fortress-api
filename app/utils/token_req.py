from flask import jsonify, request, make_response
from functools import wraps
import jwt
from jwt.exceptions import ExpiredSignatureError
from dotenv import load_dotenv
from pathlib import Path
import os


def tokenReq(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            env_path = Path(__file__).resolve().parent.parent.parent / '.env'
            load_dotenv(dotenv_path=env_path)
            secret_key = os.getenv("JWT_SECRET_KEY")
            token = None
            if "Authorization" in request.headers:
                token = request.headers["Authorization"]
            elif "jwt_token" in request.cookies:
                token = request.cookies.get("jwt_token")
            if token:
                try:
                    header = jwt.get_unverified_header(token)
                    algorithm = header['alg']
                    print(token)
                    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
                    user = payload.get("user")
                    if user and "role" in user:
                        user_role = user['role']
                        if role and user_role != role:
                            return make_response(jsonify({"status": 'fail', "message": "Unauthorized user"}), 401)
                    else:
                        return make_response(jsonify({"status": 'fail', "message": "Invalid token"}), 401)
                except ExpiredSignatureError as ex:
                    print("EXIPIRED TOKEN", f"{ex}")
                    return make_response(jsonify({"status": "fail", "message": "Expired token"}), 403)
                except Exception as ex:
                    return make_response(jsonify({"status": "fail", "message": "Invalid token"}), 401)
                return f(*args, **kwargs)
            else:
                return make_response(jsonify({"status": "fail", "message": "Unauthorized"}), 403)
        return decorated
    return decorator

