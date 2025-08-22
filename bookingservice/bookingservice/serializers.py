from rest_framework import serializers
from decimal import Decimal
from django.core.exceptions import ValidationError as DjangoValidationError
from bookingservice.models import Booking, Ticket


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for Ticket model
    """

    id = serializers.UUIDField(read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "ticket_type", "quantity", "unit_price", "subtotal"]
        read_only_fields = ["id", "unit_price", "subtotal"]


class TicketSelectionSerializer(serializers.Serializer):
    """
    Serializer for ticket selection in booking requests
    """

    ticket_type = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField(min_value=1)

    def validate_ticket_type(self, value):
        """Validate ticket type format"""
        if not value or not value.strip():
            raise serializers.ValidationError("Ticket type cannot be empty")
        return value.strip()

    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class BookingCreateSerializer(serializers.Serializer):
    """
    Serializer for creating bookings
    """

    event_id = serializers.CharField(max_length=255)
    ticket_selections = TicketSelectionSerializer(many=True)

    def validate_event_id(self, value):
        """Validate event ID format"""
        if not value or not value.strip():
            raise serializers.ValidationError("Event ID cannot be empty")
        return value.strip()

    def validate_ticket_selections(self, value):
        """Validate ticket selections"""
        if not value:
            raise serializers.ValidationError(
                "At least one ticket selection is required"
            )

        # Check for duplicate ticket types
        ticket_types = [selection["ticket_type"] for selection in value]
        if len(ticket_types) != len(set(ticket_types)):
            raise serializers.ValidationError("Duplicate ticket types are not allowed")

        return value

    def validate(self, attrs):
        """Cross-field validation"""
        # Additional validation can be added here
        return attrs


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model
    """

    id = serializers.UUIDField(read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Additional fields that might come from the booking service
    event_name = serializers.CharField(read_only=True, required=False)
    event_date = serializers.CharField(read_only=True, required=False)
    payment_details = serializers.DictField(read_only=True, required=False)

    class Meta:
        model = Booking
        fields = [
            "id",
            "event_id",
            "user_id",
            "status",
            "total_amount",
            "payment_url",
            "created_at",
            "updated_at",
            "tickets",
            "event_name",
            "event_date",
            "payment_details",
        ]
        read_only_fields = [
            "id",
            "user_id",
            "status",
            "total_amount",
            "payment_url",
            "created_at",
            "updated_at",
            "tickets",
            "event_name",
            "event_date",
            "payment_details",
        ]


class BookingResponseSerializer(serializers.Serializer):
    """
    Serializer for booking creation response
    """

    booking_id = serializers.UUIDField()
    event_id = serializers.CharField()
    user_id = serializers.CharField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_url = serializers.URLField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()
    event_name = serializers.CharField(required=False)
    event_date = serializers.CharField(required=False)
    tickets = TicketSerializer(many=True)
    payment_details = serializers.DictField(required=False)


class TicketTypeSerializer(serializers.Serializer):
    """
    Serializer for ticket type information
    """

    type = serializers.CharField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    available_quantity = serializers.IntegerField(min_value=0)
    description = serializers.CharField(required=False, allow_blank=True)


class AvailableTicketsSerializer(serializers.Serializer):
    """
    Serializer for ticket availability response
    """

    event_id = serializers.CharField()
    event_name = serializers.CharField(required=False)
    event_date = serializers.CharField(required=False)
    venue = serializers.CharField(required=False)
    ticket_types = TicketTypeSerializer(many=True)
    total_available = serializers.IntegerField(min_value=0)
    last_updated = serializers.DateTimeField()


class PaymentWebhookSerializer(serializers.Serializer):
    """
    Serializer for payment webhook payload
    """

    booking_id = serializers.UUIDField()
    payment_status = serializers.CharField()
    payment_id = serializers.CharField()
    transaction_id = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(required=False, default="USD")
    metadata = serializers.DictField(required=False)

    def validate_payment_status(self, value):
        """Validate payment status"""
        valid_statuses = [
            "completed",
            "successful",
            "paid",
            "confirmed",
            "failed",
            "cancelled",
            "expired",
            "declined",
            "pending",
            "processing",
        ]

        if value.lower() not in valid_statuses:
            raise serializers.ValidationError(f"Invalid payment status: {value}")

        return value.lower()


class BookingStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for booking status updates
    """

    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.DictField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer for error responses
    """

    error = serializers.DictField()

    def to_representation(self, instance):
        """Custom representation for error responses"""
        if isinstance(instance, dict) and "error" in instance:
            return instance

        # Handle different error types
        if isinstance(instance, serializers.ValidationError):
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": instance.detail,
                }
            }
        elif isinstance(instance, Exception):
            return {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(instance),
                    "details": {},
                }
            }

        return {
            "error": {
                "code": "UNKNOWN_ERROR",
                "message": "An unknown error occurred",
                "details": {},
            }
        }


class BookingListSerializer(serializers.Serializer):
    """
    Serializer for booking list responses
    """

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)
    results = BookingSerializer(many=True)


class BookingFilterSerializer(serializers.Serializer):
    """
    Serializer for booking list filters
    """

    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES, required=False)
    event_id = serializers.CharField(required=False)
    created_after = serializers.DateTimeField(required=False)
    created_before = serializers.DateTimeField(required=False)
    page = serializers.IntegerField(min_value=1, required=False, default=1)
    page_size = serializers.IntegerField(
        min_value=1, max_value=100, required=False, default=20
    )

    def validate(self, attrs):
        """Cross-field validation for date filters"""
        created_after = attrs.get("created_after")
        created_before = attrs.get("created_before")

        if created_after and created_before and created_after >= created_before:
            raise serializers.ValidationError(
                "created_after must be before created_before"
            )

        return attrs


class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer for health check responses
    """

    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    version = serializers.CharField(required=False)
    services = serializers.DictField(required=False)

    def to_representation(self, instance):
        """Custom representation for health check"""
        from django.utils import timezone

        base_response = {
            "status": "healthy",
            "timestamp": timezone.now(),
            "version": "1.0.0",
        }

        if isinstance(instance, dict):
            base_response.update(instance)

        return base_response
