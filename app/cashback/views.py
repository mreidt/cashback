import requests
from cashback.serializers import CompraSerializer
from core.models import Compra, Revendedor
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt import authentication

EXT_URL = 'https://mdaqk8ek5j.execute-api.us-east-1.amazonaws.com/v1/cashback'


class CompraViewSet(viewsets.ModelViewSet):
    """Manage purchases in the database"""
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_revendedor(self):
        """Return Revendedor object based on logged user"""
        return Revendedor.objects.get(user=self.request.user)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        queryset = self.queryset

        return queryset.filter(
            revendedor=self.get_revendedor()
        )

    @action(methods=['GET'], detail=False, url_path='list-purchases')
    def list_purchases(self, request):
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        queryset = self.get_queryset()
        if year and month:
            queryset = queryset.filter(date__year=year, date__month=month)
        else:
            queryset = queryset.filter(date__year=2021, date__month=8)

        serializer = CompraSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='accumulated-cashback')
    def accumulated_cashback(self, request):
        cpf = self.request.query_params.get('cpf')
        if not cpf:
            return Response(
                data='You must inform the CPF!',
                status=status.HTTP_400_BAD_REQUEST)
        cpf = ''.join(c for c in cpf if c.isdigit())
        payload = {'cpf': cpf}
        headers = {'token': 'ZXPURQOARHiMc6Y0flhRC1LVlZQVFRnm'}
        try:
            res = requests.get(
                EXT_URL,
                params=payload,
                headers=headers)
            if res.status_code == status.HTTP_200_OK:
                return Response(
                    data=res.json().get('body'),
                    status=status.HTTP_200_OK)
            return Response(status=res.status_code)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
