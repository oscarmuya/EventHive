from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views import (
    MyTokenObtainPairView,
    MyTokenRefreshView,
    RegisterUserView,
    OrganizationView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("register/", RegisterUserView.as_view(), name="register_user"),
    path("organization/", OrganizationView.as_view(), name="organization"),
]
