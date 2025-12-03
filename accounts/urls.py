# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    set_initial_password,
    request_password_reset,
    reset_password_confirm,
    AdminViewSet,
    manage_sessions,
    logout_all_devices
)

router = DefaultRouter()
router.register(r'admins', AdminViewSet, basename='admin')

urlpatterns = [
    # JWT Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # First login & password setup
    path('set-password/', set_initial_password, name='set_initial_password'),
    
    # Password reset
    path('password-reset/request/', request_password_reset, name='request_password_reset'),
    path('password-reset/confirm/', reset_password_confirm, name='reset_password_confirm'),
    
    # Session management
    path('sessions/', manage_sessions, name='manage_sessions'),
    path('logout-all-devices/', logout_all_devices, name='logout_all_devices'),
    
    # Admin management
    path('', include(router.urls)),
]