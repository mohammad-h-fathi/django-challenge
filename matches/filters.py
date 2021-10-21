from django_filters import rest_framework as filters
from .models import Team, Match


class TeamListFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    province = filters.CharFilter(field_name='province', lookup_expr='icontains')
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    league = filters.CharFilter(field_name='league', lookup_expr='exact')

    class Meta:
        model = Team
        fields = ['name', 'province', 'city', 'league']


class MatchListFilter(filters.FilterSet):
    match_date = filters.CharFilter(field_name='match_date', lookup_expr='icontains')
    match_date_after = filters.CharFilter(field_name='match_date', lookup_expr='gte')
    match_date_before = filters.CharFilter(field_name='match_date', lookup_expr='lte')
    host = filters.CharFilter(field_name='host__name', lookup_expr='icontains')
    guest = filters.CharFilter(field_name='guest__name', lookup_expr='icontains')
    league = filters.CharFilter(field_name='league__name', lookup_expr='icontains')
    season = filters.NumberFilter(field_name='season__name', lookup_expr='icontains')

    class Meta:
        model = Match
        fields = ['match_date', 'host', 'guest', 'league', 'season']
