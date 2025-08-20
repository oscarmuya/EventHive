from django.db import models
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from django.utils.text import slugify
from django.db.models import Q, CheckConstraint


class Organization(models.Model):
    remote_id = models.BigIntegerField(unique=True, db_index=True)
    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    last_synced = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return self.display_name or str(self.remote_id)


class Venue(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    capacity = models.PositiveIntegerField(null=True, blank=True)
    cover_image = models.ImageField(upload_to="event_covers/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)

    def clean(self):
        # enforce sane date ranges
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "end_time must be after start_time"})

    def __str__(self):
        return f"{self.title} ({self.start_time:%Y-%m-%d %H:%M})"

    class Meta:
        ordering = ["-start_time"]


class TicketType(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="ticket_types"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    quantity_total = models.PositiveIntegerField(default=0)
    quantity_sold = models.PositiveIntegerField(default=0)
    sales_start = models.DateTimeField(null=True, blank=True)
    sales_end = models.DateTimeField(null=True, blank=True)
    per_person_limit = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def available(self):
        return max(0, self.quantity_total - self.quantity_sold)

    def clean(self):
        if self.sales_start and self.sales_end and self.sales_end <= self.sales_start:
            raise ValidationError({"sales_end": "sales_end must be after sales_start"})
        if self.quantity_sold > self.quantity_total:
            raise ValidationError("quantity_sold cannot exceed quantity_total")

    class Meta:
        constraints = [
            CheckConstraint(check=Q(price__gte=0), name="ticket_price_nonnegative"),
            CheckConstraint(
                check=Q(quantity_total__gte=0), name="ticket_qty_total_nonnegative"
            ),
            CheckConstraint(
                check=Q(quantity_sold__gte=0), name="ticket_qty_sold_nonnegative"
            ),
            CheckConstraint(
                check=Q(quantity_sold__lte=models.F("quantity_total")),
                name="ticket_sold_lte_total",
            ),
        ]
        ordering = ["-price"]

    def __str__(self):
        return f"{self.name} - {self.event.title}"
