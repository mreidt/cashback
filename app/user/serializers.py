from core.models import Revendedor
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, status
from rest_framework.exceptions import APIException


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and returns it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Updates an user, setting a new password"""
        if validated_data.get('email', None):
            message = _(
                'Email can not be changed!'
            )
            raise serializers.ValidationError(message, code='email')
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            message = _(
                'Invalid credentials provided!'
            )
            raise serializers.ValidationError(message, code='authentication')

        attrs['user'] = user
        return attrs


class RevendedorSerializer(serializers.ModelSerializer):
    """Serializer for revendedor updates"""
    class Meta:
        model = Revendedor
        fields = ('cpf', 'name',)

    def update(self, instance, validated_data):
        if validated_data.get('cpf', None):
            message = _(
                'CPF field can not be changed!'
            )
            raise serializers.ValidationError(message, code='cpf')
        return super().update(instance, validated_data)


class UserRevendedorSerializer(serializers.ModelSerializer):
    """Serializer for revendedor object"""
    revendedor = RevendedorSerializer(required=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'revendedor')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def calculate_digit(self, cpf_digits):
        """
        Calculate CPF digit

        Formula:
        Original CPF = 945.086.080-78
        To calculate first digit, remove last 2 digits:
        945.086.080
        Multiply each number by below weights:
        [10, 9, 8, 7, 6, 5, 4, 3, 2]
        The result will be:
        [90, 36, 40, 0, 48, 30, 0, 24, 0]
        Sum the list: 268
        Divide the result by 11, and consider only the modulus: 4
        If modulus < 2, the digit will be 0
        Else, the digit will be 11 - modulus
        So, in this case, the digit will be 11 - 7 = 4

        For the second digit, the idea is the same, but you will include
        the first calculated digit:
        945.086.080-7
        And will multiply by the weights:
        [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        The rest of the operation still the same.
        """
        list2 = sorted(list(range(2, len(cpf_digits) + 2)), reverse=True)
        digit = sum([a * b for a, b in zip(cpf_digits, list2)]) % 11
        if digit < 2:
            return 0
        else:
            return 11 - digit

    def validate_cpf(self, cpf):
        """
        Validates if a CPF is valid


        If given CPF last two numbers are equal to the calculated digits,
        the CPF is valid, otherwise, it is invalid
        """
        test_cpf = ''.join(c for c in cpf if c.isdigit())
        # CPF size must be 11
        if len(test_cpf) != 11:
            return False
        # CPFs where all numbers are repeated will pass the rule,
        # but are invalid
        if len(set(test_cpf)) == 1:
            return False
        cpf_digits = [int(d) for d in test_cpf[:9]]
        first_digit = self.calculate_digit(cpf_digits)
        cpf_digits.append(first_digit)
        second_digit = self.calculate_digit(cpf_digits)
        if int(cpf[-1]) == second_digit and int(cpf[-2]) == first_digit:
            return True
        else:
            return False

    def validate(self, attrs):
        """Validate Revendedor object"""
        revendedor = attrs.get('revendedor')
        if not revendedor:
            message = _(
                'You must provide a CPF and a Name!'
            )
            raise serializers.ValidationError(message, code='revendedor')
        if not revendedor.get('cpf'):
            message = _(
                'You must provide a CPF!'
            )
            raise serializers.ValidationError(message, code='revendedor')
        if not revendedor.get('name'):
            message = _(
                'You must provide a Name!'
            )
            raise serializers.ValidationError(message, code='revendedor')
        if not self.validate_cpf(revendedor.get('cpf')):
            message = _(
                'You must provide a valid CPF!'
            )
            raise serializers.ValidationError(message, code='revendedor')
        return attrs

    def create(self, validated_data):
        """Creates a new Revendedor"""
        try:
            revendedor_data = validated_data.pop('revendedor', None)
            with transaction.atomic():
                # This must be an atomic transaction.
                # An user only will be created when the Revendedor is
                # correctly created and vice versa.
                user = get_user_model().objects.create_user(**validated_data)
                Revendedor.objects.create(
                    user=user,
                    cpf=revendedor_data.get('cpf'),
                    name=revendedor_data.get('name')
                )
                return user
        except APIException:
            raise APIException(
                detail='Failed to create a Revendedor.',
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
