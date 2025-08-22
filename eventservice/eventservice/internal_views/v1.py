from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from eventservice.models import Event, Organization
from eventservice.serializers import EventSerializer, OrganizationSerializer
from eventservice.permissions import IsInternalRequest
import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsInternalRequest])
def get_event_by_id(request, event_id):
    """Get single event by ID - Internal API"""
    try:
        event = get_object_or_404(Event, id=event_id)
        serializer = EventSerializer(event)
        return Response({"success": True, "data": serializer.data})
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsInternalRequest])
def get_events_by_user(request, user_id):
    """Get all events for a specific user - Internal API"""
    try:
        events = Event.objects.filter(user_id=user_id).order_by("-created_at")

        # Handle pagination
        page = request.GET.get("page", 1)
        limit = request.GET.get("limit", 20)

        paginator = Paginator(events, limit)
        events_page = paginator.get_page(page)

        serializer = EventSerializer(events_page, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
                "pagination": {
                    "total": paginator.count,
                    "pages": paginator.num_pages,
                    "current_page": int(page),
                    "has_next": events_page.has_next(),
                    "has_previous": events_page.has_previous(),
                },
            }
        )
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsInternalRequest])
def get_events_by_status(request, event_status):
    """Get events by status - Internal API"""
    try:
        events = Event.objects.filter(status=event_status)

        # Optional date filtering
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date:
            events = events.filter(created_at__gte=start_date)
        if end_date:
            events = events.filter(created_at__lte=end_date)

        serializer = EventSerializer(events, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": events.count()}
        )
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsInternalRequest])
def bulk_get_events(request):
    """Get multiple events by IDs - Internal API"""
    try:
        event_ids = request.data.get("event_ids", [])

        if not event_ids:
            return Response(
                {"success": False, "error": "event_ids is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        events = Event.objects.filter(id__in=event_ids)
        serializer = EventSerializer(events, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
                "found_count": events.count(),
                "requested_count": len(event_ids),
            }
        )
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsInternalRequest])
def update_event_status(request, event_id):
    """Update event status - Internal API"""
    try:
        event = get_object_or_404(Event, id=event_id)
        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {"success": False, "error": "status is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.status = new_status
        event.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "success": True,
                "message": f"event {event_id} status updated to {new_status}",
            }
        )
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
