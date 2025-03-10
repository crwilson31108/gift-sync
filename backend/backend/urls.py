"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (
    UserViewSet, FamilyViewSet, WishListViewSet,
    WishListItemViewSet, NotificationViewSet, PasswordResetViewSet, test_email
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'families', FamilyViewSet, basename='family')
router.register(r'wishlists', WishListViewSet, basename='wishlist')
router.register(r'wishlist-items', WishListItemViewSet, basename='wishlist-item')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'password-reset', PasswordResetViewSet, basename='password-reset')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/test-email/', test_email, name='test-email'),
]

# Add this to serve media files in both development and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media files in production
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
