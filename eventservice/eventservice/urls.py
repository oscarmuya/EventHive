from django.contrib import admin
from django.urls import path, include
from .views import EventsViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"events", EventsViewSet, basename="events")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
]
