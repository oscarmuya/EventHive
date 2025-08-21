from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import Event, Organization
from .serializers import EventSerializer, VenueSerializer, TicketTypeSerializer
from .permissions import IsOrganizer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import EventFilter
from utils.redis import redis_client


class EventsViewSet(ModelViewSet):
    model = Event
    serializer_class = EventSerializer
    queryset = Event.objects.all().select_related("venue")
    lookup_field = "slug"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EventFilter

    search_fields = ["title", "description", "venue__name"]
    ordering_fields = ["start_time"]
    ordering = ["start_time"]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsOrganizer()]

    def create(self, request):
        """
        Create a new event.
        1. Create a venue
        2. Create an event
        3. Create ticket types

        """
        token_payload = request.user.token_payload
        organization_id = token_payload.get("organization_id")
        if not organization_id:
            return Response(
                {
                    "error": "Organization ID not found",
                    "code": "no_organization_id",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization, _ = Organization.objects.get_or_create(remote_id=organization_id)

        venue_data = request.data.pop("venue")
        event_data = request.data.pop("event")
        ticket_types_data = request.data.pop("ticket_types")

        venue_serializer = VenueSerializer(data=venue_data)
        venue_serializer.is_valid(raise_exception=True)
        venue_serializer.save()

        event_serializer = self.get_serializer(
            data={
                **event_data,
                "venue": venue_serializer.instance.id,
                "organization": organization.id,
            }
        )
        event_serializer.is_valid(raise_exception=True)
        event_serializer.save(
            organization=organization, venue=venue_serializer.instance
        )

        for ticket_type_data in ticket_types_data:
            ticket_type_serializer = TicketTypeSerializer(
                data={
                    **ticket_type_data,
                    "event": event_serializer.instance.id,
                }
            )
            ticket_type_serializer.is_valid(raise_exception=True)
            ticket_type_serializer.save(event=event_serializer.instance)
            # Cache the event data
            redis_client.set(
                f"ticket_type:{ticket_type_serializer.instance.id}",
                ticket_type_serializer.instance.quantity,
            )

        # Cache the event data
        redis_client.set(
            f"event:{event_serializer.instance.id}",
            event_serializer.data,
        )
        return Response(
            event_serializer.data,
            status=status.HTTP_201_CREATED,
        )
