from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer
from utils.redis import redis_client
from .models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from django.utils import timezone
from decimal import Decimal
from .serializers import AvailableTicketsSerializer
from .services.event_service import event_client

logger = logging.getLogger(__name__)

use_cache = False


class BookingServiceError(Exception):
    """Base exception for booking service errors"""

    pass


@api_view(["GET"])
def get_ticket_availability(request, event_id):
    """
    Get ticket availability for an event

    GET /events/{event_id}/tickets/available/
    """
    try:
        logger.info(f"Getting ticket availability for event_id: {event_id}")
        # Get availability from booking service
        try:
            # Try cache first if enabled
            if use_cache:
                ticket_keys = redis_client.get_keys(f"{event_id}:")

                logger.info(
                    f"Found {len(ticket_keys)} cached ticket types for event_id: {event_id}"
                )
                cached_data = []
                for key in ticket_keys:
                    data = redis_client.get(key)
                    if data:
                        cached_data.append({key.split(":")[1]: data})

                if cached_data is not None:
                    logger.info(
                        f"Returning cached availability for event_id: {event_id}"
                    )
                    return Response({"data": cached_data}, status=status.HTTP_200_OK)

            # Get event details from Event Service
            event_data = event_client.get_event(event_id)

            if not event_data:
                raise BookingServiceError(f"Event {event_id} not found")

            # Check if event is bookable
            if not event_data.get("status", "").lower() == "published":
                raise BookingServiceError(f"Event {event_id} is not active for booking")

            # Check if event has tickets
            if not event_data.get("ticket_types", False):
                raise BookingServiceError(
                    f"Event {event_id} is not available for booking"
                )

            # Extract ticket types and availability
            ticket_types = event_data.get("ticket_types", [])

            # Format availability response
            availability_data = [
                {ticket["id"]: ticket["quantity_total"] - ticket["quantity_sold"]}
                for ticket in ticket_types
            ]

            # Cache the availability data
            if use_cache:
                for ticket in ticket_types:
                    redis_client.set(
                        f"{event_id}:{ticket['id']}",
                        ticket["quantity_total"] - ticket["quantity_sold"],
                        ex=3,  # Cache for 5 minutes
                    )

            logger.info(f"Successfully retrieved availability for event_id: {event_id}")
            return Response({"data": availability_data}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Unexpected error getting availability for event_id {event_id}: {e}"
            )
            raise BookingServiceError(f"Failed to get ticket availability: {e}")

    except Exception as e:
        logger.error(f"Error getting ticket availability for event_id {event_id}: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing bookings.
    """

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, *args, **kwargs):
        """
        Override the default create method to set the user_id from the request.
        """
        _user = self.request.user
        user, _ = User.objects.get_or_create(remote_id=_user.id)

    def get_queryset(self):
        """
        Restricts the returned bookings to those of the currently authenticated user.
        """
        user = self.request.user
        if user.is_authenticated:
            return self.queryset.filter(user_id=user.id)
        return self.queryset.none()
