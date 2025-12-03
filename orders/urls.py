# orders/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CountryViewSet

router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]