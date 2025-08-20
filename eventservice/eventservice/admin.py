from django.contrib import admin
from .models import Venue, Event, TicketType, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("display_name", "email", "remote_id", "last_synced")
    search_fields = ("display_name", "email", "remote_id")


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "country",
        "capacity",
    )
    search_fields = (
        "name",
        "city",
        "country",
    )
    list_filter = ("city", "country")


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organization",
        "venue",
        "start_time",
        "end_time",
        "status",
    )
    list_filter = (
        "status",
        "start_time",
        "end_time",
        "venue",
    )
    search_fields = (
        "title",
        "description",
        "organization__remote_id",
        "venue__name",
    )
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "start_time"
    inlines = [TicketTypeInline]


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "event",
        "price",
        "quantity_total",
        "quantity_sold",
        "available",
        "is_active",
    )
    list_filter = ("event", "is_active")
    search_fields = (
        "name",
        "event__title",
    )
    readonly_fields = ("quantity_sold", "available")
