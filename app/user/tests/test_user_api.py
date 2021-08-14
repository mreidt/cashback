from core.models import Revendedor
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

URL_CREATE_USER = reverse('user:create')
URL_TOKEN = reverse('token_obtain_pair')
URL_ME = reverse('user:me')
URL_CREATE_REVENDEDOR = reverse('user:create-revendedor')
URL_PROFILE = reverse('user:profile')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_revendedor(**params):
    return Revendedor.objects.create(**params)


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

        self.assertIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created with invalid credentials"""
        email = 'user1@grupoboticario.com.br'
        create_user(email=email, password='pass1234')
        payload = {'email': email, 'password': 'wrongpass123'}
        res = self.client.post(URL_TOKEN, payload)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_invalid_user(self):
        """Test that token is not created for an inexistent user"""
        payload = {
            'email': 'user1@grupoboticario.com',
            'password': 'pass1234'
        }
        res = self.client.post(URL_TOKEN, payload)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_user_details(self):
        """Test that authentication is required to get user details"""
        res = self.client.get(URL_ME)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_revendedor(self):
        """Test Revendedor object creation"""
        payload = {
            'email': 'revendedor@grupoboticario.com.br',
            'password': 'pass1234',
            'revendedor': {
                'cpf': '945.086.080-78',
                'name': 'revendedor 1'
            }
        }

        res = self.client.post(URL_CREATE_REVENDEDOR, payload, format='json')
        user = get_user_model().objects.get(email=payload.get('email'))
        revendedor = Revendedor.objects.get(user=user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.email, payload.get('email'))
        self.assertEqual(revendedor.cpf, payload.get('revendedor').get('cpf'))
        self.assertEqual(
            revendedor.name,
            payload.get('revendedor').get('name'))

    def test_create_revendedor_same_email_fails(self):
        """Test that email is unique"""
        email = 'revendedor@grupoboticario.com.br'
        payload1 = {
            'email': email,
            'password': 'pass1234',
            'revendedor': {
                'cpf': '945.086.080-78',
                'name': 'revendedor 1'
            }
        }
        payload2 = {
            'email': email,
            'password': '1234pass',
            'revendedor': {
                'cpf': '865.550.330-45',
                'name': 'revendedor 2'
            }
        }
        self.client.post(URL_CREATE_REVENDEDOR, payload1, format='json')
        res = self.client.post(URL_CREATE_REVENDEDOR, payload2, format='json')

        users = get_user_model().objects.filter(email=email)
        revendedores = Revendedor.objects.all()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(users), 1)
        self.assertEqual(len(revendedores), 1)

    def test_create_revendedor_same_cpf_fails(self):
        """Test CPF is unique"""
        cpf = '945.086.080-78'
        payload1 = {
            'email': 'revendedor1@grupoboticario.com.br',
            'password': 'pass1234',
            'revendedor': {
                'cpf': cpf,
                'name': 'revendedor 1'
            }
        }
        email2 = 'revendedor2@grupoboticario.com.br'
        payload2 = {
            'email': email2,
            'password': '1234pass',
            'revendedor': {
                'cpf': cpf,
                'name': 'revendedor 2'
            }
        }
        self.client.post(URL_CREATE_REVENDEDOR, payload1, format='json')
        res = self.client.post(URL_CREATE_REVENDEDOR, payload2, format='json')

        revendedores = Revendedor.objects.all()
        users = get_user_model().objects.filter(email=email2)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(revendedores), 1)
        self.assertEqual(len(users), 0)

    def test_authentication_revendedor_details(self):
        """Test that authentication is required to get revendedor details"""
        res = self.client.get(URL_PROFILE)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_revendedor_invalid_cpf(self):
        """Test that CPF validator is working properly"""
        email = 'revendedor@grupoboticario.com.br'
        for d in range(0, 10):
            payload = {
                'email': email,
                'password': 'pass1234',
                'revendedor': {
                    'cpf': f'{str(d)*3}.{str(d)*3}.{str(d)*3}-{str(d)*2}',
                    'name': 'revendedor 1'
                }
            }

            revendedores = Revendedor.objects.all()
            users = get_user_model().objects.filter(email=email)

            res = self.client.post(
                URL_CREATE_REVENDEDOR, payload, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(len(revendedores), 0)
            self.assertEqual(len(users), 0)


class PrivateUserApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user(
            email='sample_user@grupoboticario.com.br',
            password='password123'
        )
        self.revendedor = create_revendedor(
            user=self.user,
            cpf='493.535.620-07',
            name='revendedor sample'
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

    def test_update_user_email_fails(self):
        """Test authenticated user email fails"""
        payload = {
            'email': 'newmail@grupoboticario.com.br'
        }

        email = self.user.email
        res = self.client.patch(URL_ME, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user.email, email)

    def test_update_revendedor_profile(self):
        """Test authenticated revendedor profile update"""
        payload = {
            'name': 'change name'
        }

        res = self.client.patch(URL_PROFILE, payload)

        self.revendedor.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.revendedor.name, payload.get('name'))

    def test_update_revendedor_cpf_fails(self):
        """Test authenticated revendedor update cpf fails"""
        payload = {
            'cpf': '071.765.450-81'
        }

        cpf = self.revendedor.cpf
        res = self.client.patch(URL_PROFILE, payload)

        self.revendedor.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.revendedor.cpf, cpf)
