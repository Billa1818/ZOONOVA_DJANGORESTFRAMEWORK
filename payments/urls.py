# payments/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StripePaymentViewSet,
    create_checkout_session,
    stripe_webhook,
    verify_payment
)

router = DefaultRouter()
router.register(r'stripe', StripePaymentViewSet, basename='stripe-payment')

urlpatterns = [
    path('create-checkout/', create_checkout_session, name='create_checkout'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    path('verify/', verify_payment, name='verify_payment'),
    path('', include(router.urls)),
]