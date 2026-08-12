from django.test import TestCase
from .models import CustomUser
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from jobportal.models import Candidate

class CustomUserTest(TestCase):

    def test_create_user(self):
        user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Test@123"
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("Test@123"))



class SignupAPITest(APITestCase):

    def test_signup_candidate(self):
        data = {
            "username": "candidate1",
            "email": "candidate1@example.com",
            "phone": "1234567890",
            "password": "Test@123",
            "role": CustomUser.Role.CANDIDATE,
        }

        response = self.client.post(
            reverse("signup"),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        user = CustomUser.objects.get(
            username="candidate1"
        )

        self.assertTrue(
            user.check_password("Test@123")
        )

        self.assertTrue(
            Candidate.objects.filter(user=user).exists()
        )

    def test_signup_duplicate_email(self):
        CustomUser.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="Test@123"
        )

        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "phone": "1234567890",
            "password": "Test@123",
            "role": CustomUser.Role.CANDIDATE,
        }

        response = self.client.post(
            reverse("signup"),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


class LoginAPITest(APITestCase):

    def test_login_success(self):
        CustomUser.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="Test@123",
            role=CustomUser.Role.CANDIDATE,
        )

        data = {
            "username": "loginuser",
            "password": "Test@123",
        }

        response = self.client.post(
            reverse("login"),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        CustomUser.objects.create_user(
            username="loginuser2",
            email="login2@example.com",
            password="Test@123",
            role=CustomUser.Role.CANDIDATE,
        )

        data = {
            "username": "loginuser2",
            "password": "WrongPassword123",
        }

        response = self.client.post(
            reverse("login"),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED

        )

    def test_login_blocked_user(self):
        CustomUser.objects.create_user(
            username="blockeduser",
            email="blocked@example.com",
            password="Test@123",
            role=CustomUser.Role.CANDIDATE,
            is_blocked=True,
        )

        data = {
            "username": "blockeduser",
            "password": "Test@123",
        }

        response = self.client.post(
            reverse("login"),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "Your account has been blocked.",
            str(response.data)
        )
        
    def test_signup_does_not_expose_password(self):

        data = {
            "username": "security_user",
            "email": "security@example.com",
            "phone": "9999999999",
            "password": "Test@123",
            "role": "CANDIDATE",
        }

        response = self.client.post(
            "/api/signup/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        # Password should not appear in response
        self.assertNotIn(
            "password",
            response.data
        )