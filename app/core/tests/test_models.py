import datetime

from core import models
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase


def sample_revendedor(
        email='revendedor@grupoboticario.com.br',
        name='Revendedor Teste',
        cpf='077.282.440-19',
        password='pass123'):
    """Creates a sample revendedor"""
    return models.Revendedor.objects.create(
        user=sample_user(
            email=email,
            password=password
        ),
        name=name,
        cpf=cpf
    )


def sample_user(email='user@grupoboticario.com.br', password='pass123'):
    """Creates a sample user"""
    return get_user_model().objects.create_user(
        email=email,
        password=password
    )


class ModelTests(TestCase):

    # region User Tests
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'teste@grupoboticario.com.br'
        password = 'pass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'teste@GRUPOBOTICARIO.COM.BR'
        user = get_user_model().objects.create_user(
            email=email,
            password='pass123'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_innvalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='pass123'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email='teste@grupoboticario.com.br',
            password='pass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_users_with_same_email_fails(self):
        """Test creating two users with same email raises error"""
        email = 'repeat@grupoboticario.com.br'

        get_user_model().objects.create_user(
            email=email,
            password='pass123'
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email=email,
                password='123pass'
            )
    # endregion

    # region Revendedor Tests
    def test_create_revendedor_successful(self):
        """Test creating revendedor successful"""
        email = 'teste@grupoboticario.com.br'
        password = 'pass123'
        name = 'User 1'
        cpf = '713.765.400-29'
        user = sample_user(email=email, password=password)
        revendedor = models.Revendedor.objects.create(
            user=user,
            name=name,
            cpf=cpf
        )

        self.assertEqual(revendedor.user.email, email)
        self.assertEqual(revendedor.name, name)
        self.assertTrue(revendedor.user.check_password(password))
        self.assertEqual(revendedor.cpf, cpf)

    def test_create_revendedor_same_cpf_fails(self):
        """Test creating revendedor with same cpf raises error"""
        cpf = '713.765.400-29'
        models.Revendedor.objects.create(
            user=sample_user(),
            name='revendedor 1',
            cpf=cpf
        )

        with self.assertRaises(IntegrityError):
            models.Revendedor.objects.create(
                user=sample_user(
                    email='user2@grupoboticario.com.br',
                    password='123pass'
                ),
                name='revendedor 2',
                cpf=cpf
            )

    def test_create_revendedor_no_name(self):
        """Test creating revendedor with no name raises error"""
        with self.assertRaises(IntegrityError):
            models.Revendedor.objects.create(
                user=sample_user(),
                cpf='093.118.300-62',
                name=None
            )
    # endregion

    # region Compra Tests
    def test_create_compra_successful(self):
        """Test creating compra successful"""
        codigo = 1
        valor = 9.9
        data = datetime.datetime(2021, 5, 29)
        revendedor = sample_revendedor()

        compra = models.Compra.objects.create(
            code=codigo,
            value=valor,
            date=data,
            revendedor=revendedor
        )

        self.assertEqual(compra.code, codigo)
        self.assertEqual(compra.value, valor)
        self.assertEqual(compra.date, data)
        self.assertEqual(compra.revendedor, revendedor)

    # endregion
