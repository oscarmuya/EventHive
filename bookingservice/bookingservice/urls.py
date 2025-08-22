from django.contrib import admin
from django.urls import path, include
from bookingservice import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"bookings", views.BookingViewSet, basename="booking")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("/", include(router.urls)),
    # Ticket availability endpoint
    path(
        "events/<int:event_id>/tickets/available/",
        views.get_ticket_availability,
        name="ticket-availability",
    ),
]
