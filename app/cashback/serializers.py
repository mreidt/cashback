from core.models import Compra
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


class CompraSerializer(serializers.ModelSerializer):
    """Serializer for purchases"""

    class Meta:
        model = Compra
        fields = (
            'id',
            'code',
            'value',
            'date',
            'revendedor',
            'status',
            'cashback_percent',
            'cashback_value',
            'status_str')
        read_only_fields = ('id',)

    def validate(self, attrs):
        """Validate Compra object"""
        if attrs.get('value') <= 0:
            message = _(
                'Purchase value must be greater than 0!'
            )
            raise serializers.ValidationError(message, code='purchase')
        if attrs.get('revendedor').user != self.context.get('request').user:
            raise PermissionDenied()
        cpf = attrs.get('revendedor').cpf
        if ''.join(c for c in cpf if c.isdigit()) == '15350946056':
            attrs['status'] = 2
        else:
            attrs['status'] = 1
        return attrs
