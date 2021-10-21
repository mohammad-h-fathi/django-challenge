import django.db
import django_filters.rest_framework
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, generics, status
from rest_framework.response import Response

from .filters import TeamListFilter, MatchListFilter
from .serializers import *
from stadiums.models import Stadium


class LeagueViewSet(viewsets.ModelViewSet):
    serializer_class = LeagueSerializer
    queryset = League.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class SeasonViewSet(viewsets.ModelViewSet):
    serializer_class = SeasonSerializer
    queryset = Season.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def partial_update(self, request, *args, **kwargs):
        return Response({'message': 'Method Not Allowed', 'status': 405}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TeamsViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TeamsListSerializer
        else:
            return TeamsCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        query_set = Team.objects.all() if self.request.user.is_staff else Team.objects.filter(is_active=True)
        if self.action == 'list':
            get_filters = TeamListFilter(self.request.GET, query_set)
            return get_filters.qs
        return query_set


class TeamMatchesGenericView(generics.ListAPIView):
    serializer_class = MatchListSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = MatchListFilter

    def get_queryset(self):
        return Match.objects.filter(
            Q(guest__id=self.kwargs.get('team_id')) | Q(host__id=self.kwargs.get('team_id'))).order_by(
            'match_date').reverse()


class MatchesViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return MatchListSerializer
        else:
            return MatchCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        query_set = Match.objects.all()
        if self.action == 'list':
            get_filters = TeamListFilter(self.request.GET, query_set)
            query_set = get_filters.qs
            province = self.request.GET.get('province', None)
            stad_qs = Stadium.objects
            if province:
                stad_qs = stad_qs.filter(province__icontains=province)
            city = self.request.GET.get('city', None)
            if city:
                stad_qs = stad_qs.filter(city__icontains=province)
            stadium = self.request.GET.get('stadium', None)
            if stadium:
                stad_qs = stad_qs.filter(name__icontains=stadium)
            if isinstance(stad_qs, QuerySet):
                ids = set([std.id for std in stad_qs])
                query_set = query_set.filter(stadium__in=ids)
        return query_set

    def partial_update(self, request, *args, **kwargs):
        return Response({'message': 'Method Not Allowed', 'status': 405}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class MatchSeatsViewSet(viewsets.ModelViewSet):
    """
        Viewset for creating match seats,
        match seat can be created solo, or in rows with respecting serializers
    """
    serializer_class = MatchSeatsSerializer

    def get_queryset(self):
        return MatchSeats.objects.filter(match__id=self.kwargs.get('match_id', 0))

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        match = self.kwargs.get('match_id', 0)
        match = get_object_or_404(Match, id=match)
        data = request.data
        if data.get('solo', None):
            data = data.get('solo')
            data['match'] = match.id
            ser = MatchSeatsSerializer(data=data)
            ser.is_valid(raise_exception=True)
            instance = ser.save()
            return Response({
                'status': 201,
                'message': 'Created Successfully',
                'data': MatchSeatsSerializer(instance).data
            })
        elif data.get('rows'):
            data = data.get('rows')
            data['match'] = match.id
            ser = RowMatchSeatSerializer(data=data)
            ser.is_valid(raise_exception=True)
            ser.save()
            return Response({
                'status': 201,
                'message': 'Created Successfully',
                'data': None
            })
        else:
            raise serializers.ValidationError({'data': 'Invalid Data sent'})

    def update(self, request, *args, **kwargs):
        request.data.update({'match': kwargs.get('match_id', 0)})
        return super(MatchSeatsViewSet, self).update(request, args, kwargs)

    def patch(self, request, match_id, *args, **kwargs):
        match = get_object_or_404(Match, id=match_id)
        data = request.data
        try:
            if data.get('solo', None):
                data = data.get('solo')
                instance = get_object_or_404(MatchSeats, match=match, id=data.pop('id', 0))
                data['match'] = instance.match.id
                print(data)
                ser = MatchSeatsSerializer(data=data)
                ser.is_valid(raise_exception=True)
                print(ser.validated_data)

                instance = ser.update(instance, ser.validated_data)
                return Response({
                    'status': 200,
                    'message': 'Updated Successfully',
                    'data': MatchSeatsSerializer(instance).data
                })
            elif data.get('rows'):
                data = data.get('rows')
                data['match'] = match.id
                ser = RowMatchSeatSerializer(data=data, partial=True)
                ser.is_valid(raise_exception=True)
                ser.update(None, ser.validated_data)
                return Response({
                    'status': 200,
                    'message': 'Updated Successfully',
                    'data': None
                })
            else:
                raise serializers.ValidationError({'data': 'Invalid Data sent'})
        except django.db.utils.IntegrityError:
            return Response({'message': {
                'general': 'Seat is already defined',
            }, 'status': 400}, status=status.HTTP_400_BAD_REQUEST)

