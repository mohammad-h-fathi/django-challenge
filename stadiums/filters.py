from django_filters import rest_framework as filters
from .models import Stadium


class StadiumListFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    address = filters.CharFilter(field_name='address', lookup_expr='icontains')
    province = filters.CharFilter(field_name='province', lookup_expr='icontains')
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    capacity = filters.NumberFilter(field_name='capacity', lookup_expr='icontains')
    min_capacity = filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    max_capacity = filters.NumberFilter(field_name='capacity', lookup_expr='lte')

    class Meta:
        model = Stadium
        fields = ['name', 'address', 'province', 'city', 'capacity']
