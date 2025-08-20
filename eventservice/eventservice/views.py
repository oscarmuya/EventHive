from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import Event, Organization
from .serializers import EventSerializer, VenueSerializer, TicketTypeSerializer
from .permissions import IsOrganizer


class EventsViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizer]
    model = Event
    serializer_class = EventSerializer

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
                    "error": "Organization ID not found in token payload",
                    "code": "no_organization_id",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization, _ = Organization.objects.get_or_create(remote_id=organization_id)

        venue_data = request.data.pop("venue")
        ticket_types_data = request.data.pop("ticket_types")

        venue_serializer = VenueSerializer(data=venue_data)
        venue_serializer.is_valid(raise_exception=True)
        venue_serializer.save()

        event_serializer = self.get_serializer(data=request.data)
        event_serializer.is_valid(raise_exception=True)
        event_serializer.save(
            organization=organization, venue=venue_serializer.instance
        )

        for ticket_type_data in ticket_types_data:
            ticket_type_serializer = TicketTypeSerializer(data=ticket_type_data)
            ticket_type_serializer.is_valid(raise_exception=True)
            ticket_type_serializer.save(event=event_serializer.instance)

        return Response(event_serializer.data)
