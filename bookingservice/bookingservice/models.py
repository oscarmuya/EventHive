import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class User(models.Model):
    remote_id = models.BigIntegerField(unique=True, db_index=True)
    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    last_synced = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return self.display_name or str(self.remote_id)


class Booking(models.Model):
    """
    Booking model representing a ticket reservation for an event
    """

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(max_length=255, help_text="Event ID from Event Service")
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bookings",
        help_text="The user who made the booking",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text="Current status of the booking",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Total amount for all tickets in this booking",
    )
    payment_url = models.URLField(
        blank=True, null=True, help_text="Payment URL returned from payment service"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_id"]),
            models.Index(fields=["user_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Booking {self.id} - {self.status} - ${self.total_amount}"

    @property
    def is_pending(self):
        return self.status == self.PENDING

    @property
    def is_confirmed(self):
        return self.status == self.CONFIRMED

    @property
    def is_cancelled(self):
        return self.status == self.CANCELLED

    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return self.status in [self.PENDING, self.CONFIRMED]

    def calculate_total(self):
        """Calculate total amount from associated tickets"""
        return self.tickets.aggregate(total=models.Sum("subtotal"))["total"] or Decimal(
            "0.00"
        )


class Ticket(models.Model):
    """
    Ticket model representing individual ticket items within a booking
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="tickets",
        help_text="The booking this ticket belongs to",
    )
    ticket_type = models.CharField(
        max_length=100, help_text="Type of ticket (e.g., 'VIP', 'General', 'Student')"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], help_text="Number of tickets of this type"
    )
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Price per individual ticket",
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Total price for this ticket type (quantity * unit_price)",
    )

    class Meta:
        ordering = ["ticket_type"]
        indexes = [
            models.Index(fields=["booking"]),
            models.Index(fields=["ticket_type"]),
        ]
        # Ensure unique ticket types per booking
        unique_together = ["booking", "ticket_type"]

    def __str__(self):
        return f"{self.quantity}x {self.ticket_type} @ ${self.unit_price} each"

    def save(self, *args, **kwargs):
        """Override save to automatically calculate subtotal"""
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def clean(self):
        """Validate that subtotal matches quantity * unit_price"""
        from django.core.exceptions import ValidationError

        expected_subtotal = self.quantity * self.unit_price
        if self.subtotal != expected_subtotal:
            raise ValidationError(
                f"Subtotal {self.subtotal} does not match quantity * unit_price ({expected_subtotal})"
            )
