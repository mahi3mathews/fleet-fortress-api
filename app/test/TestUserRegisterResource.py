import unittest
from unittest.mock import MagicMock
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from app.api.user_register import UserRegisterResource
import app
import secrets


bcrypt = Bcrypt()

class TestUserRegisterResource(unittest.TestCase):

    def setUp(self):
        self.mock_user_collection = MagicMock()
        self.mock_register_codes_collection = MagicMock()
        self.user_register_resource = UserRegisterResource(
            user=self.mock_user_collection, register_codes=self.mock_register_codes_collection
        )

    def test_post_with_admin_invalid_data(self):
        mock_payload = {
            "email": "test@example.com",
            "password": "password"
        }
        self.mock_user_collection.find.return_value.count.return_value = 0
        self.mock_user_collection.insert_one.return_value.acknowledged = True

        with app.test_request_context(method='POST', json=mock_payload):
            response = self.user_register_resource.post()
            expected_response = {
                "status": "fail",
                "message": "Incomplete request. No name was provided."
            }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), expected_response)

    def test_post_with_manager_token_no_name(self):
        mock_payload = {
            "email": "test@example.com",
            "password": "password"
        }
        user_token = secrets.token_hex(10)
        hashed_token = bcrypt.generate_password_hash(user_token).decode('utf-8')
        expire_at = datetime.utcnow() + timedelta(days=1)
        self.mock_user_collection.find.return_value.count.return_value = 0
        self.mock_register_codes_collection.find_one.return_value = {"email": mock_payload["email"],
                                                                     "token":hashed_token,"expire_at":expire_at }
        self.mock_user_collection.insert_one.return_value.acknowledged = True
        with app.test_request_context('?usertoken=' + user_token, method='POST', json=mock_payload):
            response = self.user_register_resource.post()
            expected_response = {
                "status": "fail",
                "message": "Incomplete request. No name was provided."
            }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), expected_response)

    def test_post_with_admin_valid_data(self):
        mock_payload = {
            "email": "test@example.com",
            "password": "password",
            "name": "Sam"
        }
        self.mock_user_collection.find.return_value.count.return_value = 0
        self.mock_user_collection.insert_one.return_value.acknowledged = True

        with app.test_request_context(method='POST', json=mock_payload):
            response = self.user_register_resource.post()
            expected_response = {
                "status": "successful",
                "message": "Administrator registered successfully"
            }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), expected_response)

    def test_post_with_manager_token(self):
        mock_payload = {
            "email": "test@example.com",
            "password": "password",
            "name": "Sally"
        }
        user_token = secrets.token_hex(10)
        hashed_token = bcrypt.generate_password_hash(user_token).decode('utf-8')
        expire_at = datetime.utcnow() + timedelta(days=1)
        self.mock_user_collection.find.return_value.count.return_value = 0
        self.mock_register_codes_collection.find_one.return_value = {"email": mock_payload["email"],
                                                                     "token":hashed_token,"expire_at":expire_at }
        self.mock_user_collection.insert_one.return_value.acknowledged = True
        with app.test_request_context('?usertoken=' + user_token, method='POST', json=mock_payload):
            response = self.user_register_resource.post()
            print("response", response)
            expected_response = {
                "status": "successful",
                "message": "Security Manager created successfully"
            }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), expected_response)

if __name__ == '__main__':
    unittest.main()
