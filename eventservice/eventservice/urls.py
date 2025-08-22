from django.contrib import admin
from django.urls import path, include
from .views import EventsViewSet
from rest_framework import routers
from eventservice.internal_views.v1 import (
    get_event_by_id,
    get_events_by_user,
    bulk_get_events,
    get_events_by_status,
    update_event_status,
)

router = routers.DefaultRouter()
router.register(r"events", EventsViewSet, basename="events")

v1_internal_views = [
    path("events/<int:event_id>/", get_event_by_id, name="get_event_by_id"),
    path("users/<int:user_id>/events/", get_events_by_user, name="get_events_by_user"),
    path("events/bulk/", bulk_get_events, name="bulk_get_events"),
    path("events/status/", get_events_by_status, name="get_events_by_status"),
    path(
        "events/<int:event_id>/status/", update_event_status, name="update_event_status"
    ),
]

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    # intrnal endpoints
    path("internal/v1/", include(v1_internal_views)),
]
