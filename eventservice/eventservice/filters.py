import django_filters
from .models import Event


class EventFilter(django_filters.FilterSet):
    start_after = django_filters.DateTimeFilter(
        field_name="start_time", lookup_expr="gte"
    )
    start_before = django_filters.DateTimeFilter(
        field_name="start_time", lookup_expr="lte"
    )

    venue = django_filters.CharFilter(field_name="venue__name", lookup_expr="exact")

    class Meta:
        model = Event
        fields = ["status", "slug"]
