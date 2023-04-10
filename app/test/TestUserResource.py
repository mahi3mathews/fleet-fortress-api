import unittest
from unittest.mock import patch, MagicMock
from datetime import timedelta, datetime
from app.enums.roles import Roles
import app
from app.api.user import UserResource
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from pathlib import Path
import os
import jwt


bcrypt = Bcrypt()


class UserResourceTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.maxDiff = None
        self.user_collection = MagicMock()
        self.register_code_collection = MagicMock()
        self.user_resource = UserResource(user=self.user_collection, register_codes=self.register_code_collection)
        env_path = Path(__file__).resolve().parent.parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)
        self.secret_key = os.getenv("JWT_SECRET_KEY")

    @patch("secrets.token_hex", return_value='reg_token')
    def test_generate_token_success(self, mock_token_hex):
        email = "test@example.com"
        time = datetime.utcnow() + timedelta(hours=24)
        test_jwt_token = jwt.encode({
            "user": {
                "email": email,
                "id": "user_id425",
                "role": Roles.ADMIN.value
            },
            "exp": time
        }, self.secret_key)
        headers = {"Authorization": test_jwt_token}
        with app.test_request_context(method='POST', json={"email": email}, headers=headers):
            self.register_code_collection.insert_one.return_value = "insert_result"
            response = self.user_resource.generate_token()

            mock_token_hex.assert_called_once()
            self.register_code_collection.insert_one.assert_called_once()
            self.assertEqual(response.status_code, 200)
            self.assertIn("User token generated successfully", response.data.decode('utf-8'))

    def test_generate_token_invalid_email(self):
        email = 'samy94kmf.com'
        time = datetime.utcnow() + timedelta(hours=24)
        test_jwt_token = jwt.encode({
            "user": {
                "email": email,
                "id": "user_id425",
                "role": Roles.ADMIN.value
            },
            "exp": time
        }, self.secret_key)
        headers = {"Authorization": test_jwt_token}

        with app.test_request_context(method='POST', json={"email": email}, headers=headers):
            response = self.user_resource.generate_token()
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json(), {"status": "fail", "message": "Invalid email.",'data': {}})

