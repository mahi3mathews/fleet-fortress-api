from flask import request
import jwt
from dotenv import load_dotenv
from pathlib import Path
import os


def get_userid_token():
    token = None
    if "Authorization" in request.headers:
        token = request.headers["Authorization"]
    elif "jwt_token" in request.cookies:
        token = request.cookies.get("jwt_token")
    if token:
        try:
            env_path = Path(__file__).resolve().parent.parent.parent / '.env'
            load_dotenv(dotenv_path=env_path)
            secret_key = os.getenv("JWT_SECRET_KEY")
            header = jwt.get_unverified_header(token)
            algorithm = header['alg']
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            user = payload.get("user")

            if user and "id" in user:
                user_id = user["id"]
                return user_id
            else:
                return None
        except Exception as ex:
            return None
    else:
        return None
