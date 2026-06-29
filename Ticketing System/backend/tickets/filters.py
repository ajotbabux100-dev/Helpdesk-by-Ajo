import django_filters
from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    status__in = django_filters.BaseInFilter(field_name='status', lookup_expr='in')

    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'category', 'department', 'assigned_to', 'requester']
