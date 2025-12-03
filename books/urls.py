# books/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BookImageViewSet, BookVideoViewSet

router = DefaultRouter()
router.register(r'', BookViewSet, basename='book')
router.register(r'images', BookImageViewSet, basename='book-image')
router.register(r'videos', BookVideoViewSet, basename='book-video')

urlpatterns = [
    path('', include(router.urls)),
]