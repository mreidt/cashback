from datetime import date, datetime
from enum import Enum

from cashback.serializers import CompraSerializer
from core.models import Compra, Revendedor
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CASHBACK_URL = reverse('cashback:compra-list')
EXTERNAL_URL = reverse('cashback:compra-accumulated-cashback')
LIST_PURCHASES_URL = reverse('cashback:compra-list-purchases')


def sample_compra(revendedor, code, **params):
    """Create and return a sample purchase"""
    defaults = {
        'value': 1.99,
        'date': datetime.now().date(),
    }
    defaults.update(params)

    return Compra.objects.create(code=code, revendedor=revendedor, **defaults)


def sample_revendedor(user, **params):
    """Create and return a sample revendedor"""
    defaults = {
        'user': user,
        'cpf': '870.091.100-34',
        'name': 'some name'
    }
    defaults.update(params)

    return Revendedor.objects.create(**defaults)


def sample_user(**params):
    """Create and return a sample User"""
    return get_user_model().objects.create_user(**params)


class Status(Enum):
    """Enum to represent purchases Status"""
    EM_VALIDACAO = 1
    APROVADO = 2
    NAO_APROVADO = 3


class PublicCashbackApiTests(TestCase):
    """Test unauthenticated cashback API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(CASHBACK_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCashbackApiTests(TestCase):
    """Test authenticated cashback API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(
            email='sample_user@grupoboticario.com.br',
            password='password123'
        )
        self.revendedor = sample_revendedor(
            user=self.user,
            cpf='493.535.620-07',
            name='revendedor sample'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_purchases(self):
        """Test retrieving a list of purchases"""
        sample_compra(revendedor=self.revendedor, code=1)
        sample_compra(revendedor=self.revendedor, code=2)

        res = self.client.get(CASHBACK_URL)

        purchases = Compra.objects.all().order_by('date')
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_purchases_limited_to_user(self):
        """Test retrieving purchases only for authenticated revendedor"""
        user2 = sample_user(
            email='new_revendedor@grupoboticario.com.br',
            password='password123'
        )
        revendedor2 = sample_revendedor(
            user=user2,
            cpf='499.209.910-66',
            name='revendedor 2'
        )

        sample_compra(revendedor=revendedor2, code=1)
        sample_compra(revendedor=self.revendedor, code=2, value=49.99)

        res = self.client.get(CASHBACK_URL)

        purchases = Compra.objects.filter(revendedor=self.revendedor)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_purchase(self):
        """Test creating purchase"""
        payload = {
            'code': 1,
            'value': 135.9,
            'date': datetime.now().date(),
            'revendedor': self.revendedor.pk
        }
        res = self.client.post(CASHBACK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        purchase = Compra.objects.get(id=res.data.get('id'))

        for key in payload.keys():
            if key == 'revendedor':
                self.assertEqual(payload.get(key), getattr(purchase, key).pk)
            else:
                self.assertEqual(payload.get(key), getattr(purchase, key))

    def test_retrieve_purchases_with_cashback_filter_by_date(self):
        """
        Test retrieving a list of purchases and the cashback values
        filtering by date (month and year)
        """
        year = 2021
        month = 1
        day = 1
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1.0,
            date=date(
                year=year - 1,
                month=month,
                day=day))
        sample_compra(
            revendedor=self.revendedor,
            code=2,
            value=2.0,
            date=date(
                year=year - 2,
                month=month,
                day=day))
        sample_compra(
            revendedor=self.revendedor,
            code=3,
            value=3.0,
            date=date(
                year=year - 3,
                month=month,
                day=day))
        sample_compra(
            revendedor=self.revendedor,
            code=4,
            value=4.0,
            date=date(
                year=year,
                month=month,
                day=day))
        sample_compra(
            revendedor=self.revendedor,
            code=5,
            value=5.0,
            date=date(
                year=year,
                month=month,
                day=day))

        res = self.client.get(
            LIST_PURCHASES_URL, {
                'year': year, 'month': month})

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=year,
            date__month=month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_purchases_with_cashback_filter_no_parameters(self):
        """
        Test retrieving a list of purchases and the cashback values
        filtering with no parameters (must return current month purchases)
        """
        year = 2020
        month = 1
        day = 1
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1.0,
            date=date(
                year=year,
                month=month,
                day=day))
        sample_compra(
            revendedor=self.revendedor,
            code=2,
            value=2.0,
            date=date(
                year=year,
                month=month,
                day=day))
        sample_compra(
            revendedor=self.revendedor,
            code=3,
            value=3.0,
            date=date(
                year=year,
                month=month,
                day=day))
        sample_compra(
            revendedor=self.revendedor,
            code=4,
            value=4.0,
            date=datetime.now().date())
        sample_compra(
            revendedor=self.revendedor,
            code=5,
            value=5.0,
            date=datetime.now().date())

        res = self.client.get(LIST_PURCHASES_URL)

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=datetime.now().date().year,
            date__month=datetime.now().date().month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_purchases_cashback_tier1(self):
        """
        Test retrieving the purchases in cashback tier 1

        Tier   - monthly purchases           - cashback
        1      - up to 1.000                 - 10%
        2      - 1.000-1.500                 - 15%
        3      - > 1.500                     - 20%
        """
        year = 2020
        month = 1
        day = 1
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1.0,
            date=date(
                year=year,
                month=month,
                day=day))

        res = self.client.get(
            LIST_PURCHASES_URL, {
                'year': year, 'month': month})

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=year,
            date__month=month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0].get('cashback_percent'), 10)
        value = res.data[0].get('value')
        self.assertEqual(
            res.data[0].get('cashback_value'), round(
                value * 0.1, 2))

    def test_retrieve_purchases_cashback_tier2(self):
        """
        Test retrieving the purchases in cashback tier 2

        Tier   - monthly purchases           - cashback
        1      - up to 1.000                 - 10%
        2      - 1.000-1.500                 - 15%
        3      - > 1.500                     - 20%
        """
        year = 2021
        month = 10
        day = 1
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1100,
            date=date(
                year=year,
                month=month,
                day=day))

        res = self.client.get(
            LIST_PURCHASES_URL, {
                'year': year, 'month': month})

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=year,
            date__month=month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0].get('cashback_percent'), 15)
        value = res.data[0].get('value')
        self.assertEqual(
            res.data[0].get('cashback_value'), round(
                value * 0.15, 2))

    def test_retrieve_purchases_cashback_tier3(self):
        """
        Test retrieving the purchases in cashback tier 3

        Tier   - monthly purchases           - cashback
        1      - up to 1.000                 - 10%
        2      - 1.000-1.500                 - 15%
        3      - > 1.500                     - 20%
        """
        year = 2021
        month = 3
        day = 5
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1600,
            date=date(
                year=year,
                month=month,
                day=day))

        res = self.client.get(
            LIST_PURCHASES_URL, {
                'year': year, 'month': month})

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=year,
            date__month=month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0].get('cashback_percent'), 20)
        value = res.data[0].get('value')
        self.assertEqual(
            res.data[0].get('cashback_value'), round(
                value * 0.2, 2))

    def test_tier1_cashback_limit(self):
        """
        Test tier1 cashback limit

        Tier   - monthly purchases           - cashback
        1      - up to 1.000                 - 10%
        2      - 1.000-1.500                 - 15%
        3      - > 1.500                     - 20%
        """
        year = 2020
        month = 9
        day = 15
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1000.0,
            date=date(
                year=year,
                month=month,
                day=day))

        res = self.client.get(
            LIST_PURCHASES_URL, {
                'year': year, 'month': month})

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=year,
            date__month=month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0].get('cashback_percent'), 10)
        value = res.data[0].get('value')
        self.assertEqual(
            res.data[0].get('cashback_value'), round(
                value * 0.1, 2))

    def test_tier2_cashback_lower_limit(self):
        """
        Test tier2 cashback lower limit

        Tier   - monthly purchases           - cashback
        1      - up to 1.000                 - 10%
        2      - 1.000-1.500                 - 15%
        3      - > 1.500                     - 20%
        """
        year = 2021
        month = 5
        day = 17
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1000.01,
            date=date(
                year=year,
                month=month,
                day=day))

        res = self.client.get(
            LIST_PURCHASES_URL, {
                'year': year, 'month': month})

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=year,
            date__month=month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0].get('cashback_percent'), 15)
        value = res.data[0].get('value')
        self.assertEqual(
            res.data[0].get('cashback_value'), round(
                value * 0.15, 2))

    def test_tier2_cashback_upper_limit(self):
        """
        Test tier2 cashback upper limit

        Tier   - monthly purchases           - cashback
        1      - up to 1.000                 - 10%
        2      - 1.000-1.500                 - 15%
        3      - > 1.500                     - 20%
        """
        year = 2019
        month = 7
        day = 8
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1500.0,
            date=date(
                year=year,
                month=month,
                day=day))

        res = self.client.get(
            LIST_PURCHASES_URL, {
                'year': year, 'month': month})

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=year,
            date__month=month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0].get('cashback_percent'), 15)
        value = res.data[0].get('value')
        self.assertEqual(
            res.data[0].get('cashback_value'), round(
                value * 0.15, 2))

    def test_tier3_cashback_limit(self):
        """
        Test tier3 cashback limit

        Tier   - monthly purchases           - cashback
        1      - up to 1.000                 - 10%
        2      - 1.000-1.500                 - 15%
        3      - > 1.500                     - 20%
        """
        year = 2015
        month = 9
        day = 4
        sample_compra(
            revendedor=self.revendedor,
            code=1,
            value=1500.01,
            date=date(
                year=year,
                month=month,
                day=day))

        res = self.client.get(
            LIST_PURCHASES_URL, {
                'year': year, 'month': month})

        purchases = Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=year,
            date__month=month)
        serializer = CompraSerializer(purchases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0].get('cashback_percent'), 20)
        value = res.data[0].get('value')
        self.assertEqual(
            res.data[0].get('cashback_value'), round(
                value * 0.2, 2))

    def test_compra_value_greater_than_zero(self):
        """
        Test that compra object validates value correctly (greater than 0)
        """
        payload = {
            'code': 1,
            'value': 0.0,
            'date': datetime.now().date(),
            'revendedor': self.revendedor.pk
        }
        res = self.client.post(CASHBACK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_compra_same_code_fails(self):
        """Test that code is unique"""
        sample_compra(revendedor=self.revendedor, code=1)
        payload = {
            'code': 1,
            'value': 0.0,
            'date': datetime.now().date(),
            'revendedor': self.revendedor.pk
        }
        res = self.client.post(CASHBACK_URL, payload)

        purchases = Compra.objects.all()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(purchases), 1)

    def test_compra_status_ok(self):
        """
        Test the status of a purchase
        must return 1 (em validação)
        """
        sample_compra(revendedor=self.revendedor, code=1)

        res = self.client.get(LIST_PURCHASES_URL)

        self.assertEqual(res.data[0].get('status'), Status.EM_VALIDACAO.value)

    def test_compra_status_aprovado(self):
        """
        Test the status of a purchase
        must return 2 (aprovado)
        """
        user2 = sample_user(
            email='another_user@grupoboticario.com.br',
            password='newpassword123'
        )
        revendedor2 = sample_revendedor(
            user=user2,
            cpf='153.509.460-56'
        )
        payload = {
            'code': 1,
            'value': 1.0,
            'date': datetime.now().date(),
            'revendedor': revendedor2.pk
        }
        self.client.force_authenticate(user=user2)
        res = self.client.post(CASHBACK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.get(LIST_PURCHASES_URL)

        self.assertEqual(res.data[0].get('status'), Status.APROVADO.value)

    def test_authenticated_compra_creation(self):
        """Test creating purchase for another revendedor"""
        user2 = sample_user(
            email='another_user@grupoboticario.com.br',
            password='newpassword123'
        )
        revendedor2 = sample_revendedor(
            user=user2,
            cpf='153.509.460-56'
        )
        payload = {
            'code': 1,
            'value': 1.0,
            'date': datetime.now().date(),
            'revendedor': revendedor2.pk
        }

        res = self.client.post(CASHBACK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_external_api_call(self):
        """Test the external API call"""
        res = self.client.get(EXTERNAL_URL, {'cpf': '230.505.760-14'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_compra_status(self):
        """
        Test that creating a Compra object with different status, always
        returns correct status
        """
        payload = {
            'code': 1,
            'value': 1.0,
            'date': datetime.now().date(),
            'revendedor': self.revendedor.pk,
            'status': 2
        }
        res = self.client.post(CASHBACK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.get(LIST_PURCHASES_URL)

        self.assertEqual(res.data[0].get('status'), Status.EM_VALIDACAO.value)
