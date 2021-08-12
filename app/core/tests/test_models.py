from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class ModelTests(TestCase):

    # region User Tests
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'teste@grupoboticario.com.br'
        password = 'pass123'
        name = 'User 1'
        cpf = '763.416.260-45'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name,
            cpf=cpf
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.name, name)
        self.assertEqual(user.cpf, cpf)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'teste@GRUPOBOTICARIO.COM.BR'
        user = get_user_model().objects.create_user(
            email=email,
            password='pass123',
            name='user 1',
            cpf='458.803.680-76'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_innvalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='pass123',
                name='name',
                cpf='713.765.400-29'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email='teste@grupoboticario.com.br',
            password='pass123',
            name='super user 1',
            cpf='495.592.240-69'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_users_with_same_email_fails(self):
        """Test creating two users with same email raises error"""
        email = 'repeat@grupoboticario.com.br'

        get_user_model().objects.create_user(
            email=email,
            password='pass123',
            name='user 1',
            cpf='458.803.680-76'
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email=email,
                password='123pass',
                name='user 2',
                cpf='446.389.490-53'
            )

    def test_create_users_with_same_cpf_fails(self):
        """Test creating two users with same cpf raises error"""
        cpf = '446.389.490-53'

        get_user_model().objects.create_user(
            email='user@grupoboticario.com.br',
            password='pass123',
            name='user 1',
            cpf=cpf
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email='user2@grupoboticario.com.br',
                password='123pass',
                name='user 2',
                cpf=cpf
            )
    # endregion
