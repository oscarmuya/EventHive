import uuid
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from bookingservice.models import Booking, Ticket


class BookingModelTest(TestCase):
    """Test cases for the Booking model"""

    def setUp(self):
        """Set up test data"""
        self.booking_data = {
            "event_id": "event_123",
            "user_id": "user_456",
            "total_amount": Decimal("150.00"),
        }

    def test_booking_creation(self):
        """Test basic booking creation"""
        booking = Booking.objects.create(**self.booking_data)

        self.assertIsInstance(booking.id, uuid.UUID)
        self.assertEqual(booking.event_id, "event_123")
        self.assertEqual(booking.user_id, "user_456")
        self.assertEqual(booking.status, Booking.PENDING)
        self.assertEqual(booking.total_amount, Decimal("150.00"))
        self.assertIsNone(booking.payment_url)
        self.assertIsNotNone(booking.created_at)
        self.assertIsNotNone(booking.updated_at)

    def test_booking_status_choices(self):
        """Test booking status choices"""
        booking = Booking.objects.create(**self.booking_data)

        # Test pending status
        self.assertTrue(booking.is_pending)
        self.assertFalse(booking.is_confirmed)
        self.assertFalse(booking.is_cancelled)

        # Test confirmed status
        booking.status = Booking.CONFIRMED
        booking.save()
        self.assertFalse(booking.is_pending)
        self.assertTrue(booking.is_confirmed)
        self.assertFalse(booking.is_cancelled)

        # Test cancelled status
        booking.status = Booking.CANCELLED
        booking.save()
        self.assertFalse(booking.is_pending)
        self.assertFalse(booking.is_confirmed)
        self.assertTrue(booking.is_cancelled)

    def test_can_be_cancelled(self):
        """Test booking cancellation logic"""
        booking = Booking.objects.create(**self.booking_data)

        # Pending booking can be cancelled
        self.assertTrue(booking.can_be_cancelled())

        # Confirmed booking can be cancelled
        booking.status = Booking.CONFIRMED
        self.assertTrue(booking.can_be_cancelled())

        # Cancelled booking cannot be cancelled again
        booking.status = Booking.CANCELLED
        self.assertFalse(booking.can_be_cancelled())

    def test_booking_string_representation(self):
        """Test booking string representation"""
        booking = Booking.objects.create(**self.booking_data)
        expected_str = f"Booking {booking.id} - pending - $150.00"
        self.assertEqual(str(booking), expected_str)

    def test_booking_ordering(self):
        """Test booking ordering by created_at descending"""
        booking1 = Booking.objects.create(
            event_id="event_1", user_id="user_1", total_amount=Decimal("100.00")
        )
        booking2 = Booking.objects.create(
            event_id="event_2", user_id="user_2", total_amount=Decimal("200.00")
        )

        bookings = list(Booking.objects.all())
        self.assertEqual(bookings[0], booking2)  # Most recent first
        self.assertEqual(bookings[1], booking1)

    def test_calculate_total_empty_booking(self):
        """Test calculate_total with no tickets"""
        booking = Booking.objects.create(**self.booking_data)
        self.assertEqual(booking.calculate_total(), Decimal("0.00"))


class TicketModelTest(TestCase):
    """Test cases for the Ticket model"""

    def setUp(self):
        """Set up test data"""
        self.booking = Booking.objects.create(
            event_id="event_123", user_id="user_456", total_amount=Decimal("150.00")
        )
        self.ticket_data = {
            "booking": self.booking,
            "ticket_type": "VIP",
            "quantity": 2,
            "unit_price": Decimal("75.00"),
        }

    def test_ticket_creation(self):
        """Test basic ticket creation"""
        ticket = Ticket.objects.create(**self.ticket_data)

        self.assertIsInstance(ticket.id, uuid.UUID)
        self.assertEqual(ticket.booking, self.booking)
        self.assertEqual(ticket.ticket_type, "VIP")
        self.assertEqual(ticket.quantity, 2)
        self.assertEqual(ticket.unit_price, Decimal("75.00"))
        self.assertEqual(ticket.subtotal, Decimal("150.00"))  # Auto-calculated

    def test_ticket_subtotal_calculation(self):
        """Test automatic subtotal calculation on save"""
        ticket = Ticket.objects.create(**self.ticket_data)
        expected_subtotal = (
            self.ticket_data["quantity"] * self.ticket_data["unit_price"]
        )
        self.assertEqual(ticket.subtotal, expected_subtotal)

    def test_ticket_subtotal_update(self):
        """Test subtotal recalculation when quantity or price changes"""
        ticket = Ticket.objects.create(**self.ticket_data)

        # Update quantity
        ticket.quantity = 3
        ticket.save()
        self.assertEqual(ticket.subtotal, Decimal("225.00"))

        # Update unit price
        ticket.unit_price = Decimal("100.00")
        ticket.save()
        self.assertEqual(ticket.subtotal, Decimal("300.00"))

    def test_ticket_string_representation(self):
        """Test ticket string representation"""
        ticket = Ticket.objects.create(**self.ticket_data)
        expected_str = "2x VIP @ $75.00 each"
        self.assertEqual(str(ticket), expected_str)

    def test_ticket_validation_positive_quantity(self):
        """Test that quantity must be positive"""
        with self.assertRaises(ValidationError):
            ticket = Ticket(
                booking=self.booking,
                ticket_type="General",
                quantity=0,  # Invalid
                unit_price=Decimal("50.00"),
            )
            ticket.full_clean()

    def test_ticket_validation_positive_price(self):
        """Test that unit_price must be positive"""
        with self.assertRaises(ValidationError):
            ticket = Ticket(
                booking=self.booking,
                ticket_type="General",
                quantity=1,
                unit_price=Decimal("0.00"),  # Invalid
            )
            ticket.full_clean()

    def test_unique_ticket_type_per_booking(self):
        """Test that ticket types must be unique per booking"""
        Ticket.objects.create(**self.ticket_data)

        # Try to create another ticket with same type for same booking
        with self.assertRaises(IntegrityError):
            Ticket.objects.create(**self.ticket_data)

    def test_ticket_clean_method(self):
        """Test ticket clean method validates subtotal"""
        ticket = Ticket(**self.ticket_data)
        ticket.subtotal = Decimal("999.99")  # Wrong subtotal

        with self.assertRaises(ValidationError):
            ticket.clean()

    def test_multiple_tickets_per_booking(self):
        """Test creating multiple different ticket types for one booking"""
        # Create VIP ticket
        vip_ticket = Ticket.objects.create(**self.ticket_data)

        # Create General ticket
        general_ticket = Ticket.objects.create(
            booking=self.booking,
            ticket_type="General",
            quantity=3,
            unit_price=Decimal("50.00"),
        )

        # Verify both tickets exist
        self.assertEqual(self.booking.tickets.count(), 2)
        self.assertIn(vip_ticket, self.booking.tickets.all())
        self.assertIn(general_ticket, self.booking.tickets.all())


class BookingTicketIntegrationTest(TestCase):
    """Integration tests for Booking and Ticket models"""

    def setUp(self):
        """Set up test data"""
        self.booking = Booking.objects.create(
            event_id="event_123",
            user_id="user_456",
            total_amount=Decimal("0.00"),  # Will be calculated
        )

    def test_calculate_total_with_tickets(self):
        """Test calculate_total with multiple tickets"""
        # Create tickets
        Ticket.objects.create(
            booking=self.booking,
            ticket_type="VIP",
            quantity=2,
            unit_price=Decimal("100.00"),
        )
        Ticket.objects.create(
            booking=self.booking,
            ticket_type="General",
            quantity=3,
            unit_price=Decimal("50.00"),
        )

        # Calculate total
        total = self.booking.calculate_total()
        expected_total = Decimal("200.00") + Decimal("150.00")  # 2*100 + 3*50
        self.assertEqual(total, expected_total)

    def test_booking_deletion_cascades_tickets(self):
        """Test that deleting booking deletes associated tickets"""
        # Create tickets
        Ticket.objects.create(
            booking=self.booking,
            ticket_type="VIP",
            quantity=1,
            unit_price=Decimal("100.00"),
        )

        # Verify ticket exists
        self.assertEqual(Ticket.objects.count(), 1)

        # Delete booking
        self.booking.delete()

        # Verify ticket is also deleted
        self.assertEqual(Ticket.objects.count(), 0)

    def test_ticket_ordering(self):
        """Test ticket ordering by ticket_type"""
        # Create tickets in reverse alphabetical order
        Ticket.objects.create(
            booking=self.booking,
            ticket_type="VIP",
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        Ticket.objects.create(
            booking=self.booking,
            ticket_type="General",
            quantity=1,
            unit_price=Decimal("50.00"),
        )

        tickets = list(self.booking.tickets.all())
        self.assertEqual(tickets[0].ticket_type, "General")  # Alphabetically first
        self.assertEqual(tickets[1].ticket_type, "VIP")
