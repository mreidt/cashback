from core import models
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase


class ModelTests(TestCase):

    # region User Tests
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'teste@grupoboticario.com.br'
        password = 'pass123'
        name = 'User 1'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.name, name)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'teste@GRUPOBOTICARIO.COM.BR'
        user = get_user_model().objects.create_user(
            email=email,
            password='pass123',
            name='user 1'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_innvalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='pass123',
                name='name'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email='teste@grupoboticario.com.br',
            password='pass123',
            name='super user 1'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_users_with_same_email_fails(self):
        """Test creating two users with same email raises error"""
        email = 'repeat@grupoboticario.com.br'

        get_user_model().objects.create_user(
            email=email,
            password='pass123',
            name='user 1'
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email=email,
                password='123pass',
                name='user 2'
            )
    # endregion

    # region Revendedor Tests
    def test_create_revendedor_successful(self):
        """Test creating revendedor successful"""
        email = 'teste@grupoboticario.com.br'
        password = 'pass123'
        name = 'User 1'
        cpf = '713.765.400-29'
        user = models.Revendedor.objects.create_user(
            email=email,
            password=password,
            name=name,
            cpf=cpf
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.name, name)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.cpf, cpf)

    def test_create_revendedor_same_cpf_fails(self):
        """Test creating revendedor with same cpf raises error"""
        cpf = '713.765.400-29'
        models.Revendedor.objects.create_user(
            email='user1@grupoboticario.com.br',
            password='pass123',
            name='revendedor 1',
            cpf=cpf
        )

        with self.assertRaises(IntegrityError):
            models.Revendedor.objects.create_user(
                email='user2@grupoboticario.com.br',
                password='123pass',
                name='revendedor 2',
                cpf=cpf
            )

    def test_create_revendedor_same_email_fails(self):
        """Test creating revendedor with same email raises error"""
        email = 'revendedor@grupoboticario.com.br'
        models.Revendedor.objects.create_user(
            email=email,
            password='pass123',
            name='revendedor 1',
            cpf='761.563.350-80'
        )

        with self.assertRaises(IntegrityError):
            models.Revendedor.objects.create_user(
                email=email,
                password='123pass',
                name='revendedor 2',
                cpf='093.118.300-62'
            )

    # endregion
