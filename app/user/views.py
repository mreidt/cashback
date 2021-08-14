from core.models import Revendedor
from rest_framework import authentication, generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings
from user.serializers import (AuthTokenSerializer, RevendedorSerializer,
                              UserRevendedorSerializer, UserSerializer)


class CreateUserView(generics.CreateAPIView):
    """Create a new user"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new authentication token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return the user"""
        return self.request.user


class CreateRevendedorView(generics.ListCreateAPIView):
    """Create a new revendedor"""
    serializer_class = UserRevendedorSerializer
    queryset = Revendedor.objects.all()

    def post(self, request, format=None):
        """Create a new Revendedor"""
        serializer = UserRevendedorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageRevendedorView(generics.RetrieveUpdateAPIView):
    """Manage authenticated revendedor"""
    serializer_class = RevendedorSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return the Revendedor"""
        return Revendedor.objects.get(user=self.request.user)
