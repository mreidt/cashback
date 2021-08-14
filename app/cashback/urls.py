from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cashback import views

router = DefaultRouter()
router.register('cashback', views.CompraViewSet)

app_name = 'cashback'
urlpatterns = [
    path('', include(router.urls))
]
