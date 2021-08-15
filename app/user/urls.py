from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path(
        'create/',
        views.CreateUserView.as_view(),
        name='create'),
    path(
        'me/',
        views.ManageUserView.as_view(),
        name='me'),
    path(
        'create-revendedor/',
        views.CreateRevendedorView.as_view(),
        name='create-revendedor'),
    path('profile', views.ManageRevendedorView.as_view(), name='profile'),
]
