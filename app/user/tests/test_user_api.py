from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

URL_CREATE_USER = reverse('user:create')
URL_TOKEN = reverse('user:token')
URL_ME = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test public user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """Test successful user creation"""
        payload = {
            'email': 'user1@grupoboticario.com.br',
            'password': 'pass1234'
        }
        res = self.client.post(URL_CREATE_USER, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload.get('password')))
        self.assertNotIn('password', res.data)

    def test_user_already_exists(self):
        """Test creation of an existent user fails"""
        payload = {
            'email': 'user1@grupoboticario.com.br',
            'password': 'pass1234'
        }
        create_user(**payload)

        res = self.client.post(URL_CREATE_USER, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password have at least 8 characters"""
        payload = {
            'email': 'user1@grupoboticario.com.br',
            'password': '1234567'
        }
        res = self.client.post(URL_CREATE_USER, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload.get('email')).exists()
        self.assertFalse(user_exists)

    def test_create_token(self):
        """Test token creation"""
        payload = {
            'email': 'user1@grupoboticario.com.br',
            'password': 'pass1234'
        }
        create_user(**payload)
        res = self.client.post(URL_TOKEN, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created with invalid credentials"""
        email = 'user1@grupoboticario.com.br'
        create_user(email=email, password='pass1234')
        payload = {'email': email, 'password': 'wrongpass123'}
        res = self.client.post(URL_TOKEN, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_invalid_user(self):
        """Test that token is not created for an inexistent user"""
        payload = {
            'email': 'user1@grupoboticario.com',
            'password': 'pass1234'
        }
        res = self.client.post(URL_TOKEN, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_user_details(self):
        """Test that authentication is required to get user details"""
        res = self.client.get(URL_ME)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user(
            email='sample_user@grupoboticario.com.br',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_profile_success(self):
        """Test authenticated user profile get"""
        res = self.client.get(URL_ME)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'email': self.user.email})

    def test_post_not_allowed_personal_page(self):
        """Test POST method on user profile page"""
        res = self.client.post(URL_ME, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test authenticated user profile update"""
        payload = {
            'password': 'newpassword999'
        }

        res = self.client.patch(URL_ME, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload.get('password')))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
