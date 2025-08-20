from rest_framework import serializers
from .models import Organization, Venue, Event, TicketType


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = "__all__"


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    venue_details = VenueSerializer(source="venue", read_only=True)
    organization_details = OrganizationSerializer(source="organization", read_only=True)
    ticket_types = TicketTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = "__all__"
