from core.models import Revendedor
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt import authentication
from user.serializers import (RevendedorSerializer, UserRevendedorSerializer,
                              UserSerializer)


class CreateUserView(generics.CreateAPIView):
    """Create a new user"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return the user"""
        return self.request.user


class CreateRevendedorView(generics.CreateAPIView):
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
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return the Revendedor"""
        return Revendedor.objects.get(user=self.request.user)
