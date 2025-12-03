"""
URL configuration for zoonova project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from books.views import BookVideoViewSet


router = routers.DefaultRouter()
router.register(r'book-videos', BookVideoViewSet, basename='book-video')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        path('auth/', include('accounts.urls')),
        path('books/', include('books.urls')),
        path('orders/', include('orders.urls')),
        path('payments/', include('payments.urls')),
        path('contact/', include('contact.urls')),
        path('', include(router.urls)),
    ])),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

# Router principal
router = routers.DefaultRouter()


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)