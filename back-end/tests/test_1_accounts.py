import requests
import unittest

class TestAccounts(unittest.TestCase):
    # Use container names
    BASE_URL_REGISTRATION = "http://account_registration:5001"
    BASE_URL_LOGIN = "http://account_login:5002"

    def setUp(self):
        self.full_name = "Test User"
        self.email = "test@fakecompany.co.uk"
        self.password = "testpassword"
        self.invalid_email = "test@invalid.com"
        self.existing_email = "existing@fakecompany.co.uk"
        self.wrong_password = "wrongpassword"

    def test_1_register(self):
        # Register the user
        register_response = requests.post(f"{self.BASE_URL_REGISTRATION}/register", headers={
            'name': self.full_name,
            'email': self.email,
            'password': self.password
        })
        if register_response.status_code != 201:
            print("Make sure the SQL volume was deleted and reset before testing")
        self.assertEqual(register_response.status_code, 201)
        self.assertIn("User registered successfully", register_response.json().get("message"))

    def test_2_login(self):
        # Login with the registered user
        login_response = requests.post(f"{self.BASE_URL_LOGIN}/login", headers={
            'email': self.email,
            'password': self.password
        })
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Login successful", login_response.json().get("message"))

        # Validate the cookie
        session_id = login_response.cookies.get('session_id')
        validate_response = requests.get(f"{self.BASE_URL_LOGIN}/validate_cookie", headers={
            'session-id': session_id
        })
        self.assertEqual(validate_response.status_code, 200)
        self.assertIn("Cookie is valid", validate_response.json().get("message"))
        self.assertEqual(validate_response.json().get("email"), self.email)

    def test_3_invalid_email_registration(self):
        # Attempt to register with an invalid email
        register_response = requests.post(f"{self.BASE_URL_REGISTRATION}/register", headers={
            'name': self.full_name,
            'email': self.invalid_email,
            'password': self.password
        })
        self.assertEqual(register_response.status_code, 400)
        self.assertIn("Email must end with '@fakecompany.co.uk'", register_response.json().get("error"))

    def test_4_wrong_password_login(self):
        # Attempt to login with the wrong password
        login_response = requests.post(f"{self.BASE_URL_LOGIN}/login", headers={
            'email': self.email,
            'password': self.wrong_password
        })
        self.assertEqual(login_response.status_code, 401)
        self.assertIn("Invalid email or password", login_response.json().get("error"))

    def test_5_existing_email_registration(self):
        # Attempt to register with the same email again
        register_response = requests.post(f"{self.BASE_URL_REGISTRATION}/register", headers={
            'name': self.full_name,
            'email': self.email,
            'password': self.password
        })
        self.assertEqual(register_response.status_code, 500)
        self.assertIn("Duplicate entry", register_response.json().get("error"))

    def test_6_logout(self):
        # Login with the registered user
        login_response = requests.post(f"{self.BASE_URL_LOGIN}/login", headers={
            'email': self.email,
            'password': self.password
        })
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Login successful", login_response.json().get("message"))

        # Logout the user
        session_id = login_response.cookies.get('session_id')
        logout_response = requests.post(f"{self.BASE_URL_LOGIN}/logout", headers={
            'session-id': session_id
        })
        self.assertEqual(logout_response.status_code, 200)
        self.assertIn("Logout successful", logout_response.json().get("message"))

        # Validate the cookie after logout
        validate_response = requests.get(f"{self.BASE_URL_LOGIN}/validate_cookie", headers={
            'session-id': session_id
        })
        self.assertEqual(validate_response.status_code, 401)
        self.assertIn("Invalid cookie", validate_response.json().get("error"))

if __name__ == '__main__':
    unittest.main()