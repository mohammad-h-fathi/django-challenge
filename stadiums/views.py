import django.db
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import StadiumListFilter
from .serializers import *


class StadiumsViewSet(viewsets.ModelViewSet):
    serializer_class = StadiumSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        query_set = Stadium.objects.all() if self.request.user.is_staff else Stadium.objects.filter(is_active=True)
        if self.action == 'list':
            get_filters = StadiumListFilter(self.request.GET, query_set)
            return get_filters.qs
        return query_set


class StadiumSeatsView(viewsets.ViewSet):

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, stadium):
        stadium = get_object_or_404(Stadium, id=stadium)
        paginator = PageNumberPagination()
        paginator.page_query_param = 'page'
        paginator.page_size = 50
        paginated_qs =paginator.paginate_queryset(StadiumSeats.objects.filter(stadium=stadium), request)
        ser_data = StadiumSeatSerializer(paginated_qs, many=True)
        paginated_resp = paginator.get_paginated_response(ser_data.data)
        return paginated_resp

    def create(self, request, stadium):
        stadium = get_object_or_404(Stadium, id=stadium)
        data = request.data
        if data.get('solo', None):
            data = data.get('solo', None)
            data['stadium'] = stadium.pk
            ser = StadiumSeatSerializer(data=data)
            ser.is_valid(raise_exception=True)
            instance = ser.save()
            resp = {
                "data": StadiumSeatSerializer(instance).data,
                "message": "Created Successfully",
                "status": 201
            }
            return Response(resp, status=status.HTTP_201_CREATED)
        elif data.get('group', None):
            data = data.get('group', None)
            data['stadium'] = stadium.pk
            ser = SeatsGroupSerializer(data=data)

        elif data.get('column_only', None):
            data = data.get('column_only', None)
            data['stadium'] = stadium.pk
            ser = SeatsColumnOnlySerializer(data=data)
        elif data.get('row_only', None):
            data = data.get('row_only', None)
            data['stadium'] = stadium.pk
            ser = SeatsRowOnlySerializer(data=data)
        else:
            raise serializers.ValidationError({'general': 'no post data is sent'})
        ser.is_valid(raise_exception=True)
        try:
            ser.save()
            resp = {
                "data": None,
                "message": "Seats Created Successfully",
                "status": 201
            }
            return Response(resp, status=status.HTTP_201_CREATED)
        except django.db.IntegrityError:
            resp = {
                "data": None,
                "message": "There is seat with the given info exists",
                "status": 400
            }
            return Response(resp, status=status.HTTP_201_CREATED)

    def update(self, request, stadium, pk):
        stadium = get_object_or_404(Stadium, id=stadium)
        seat = get_object_or_404(StadiumSeats, pk=pk, stadium=stadium)
        data = request.data
        data['stadium'] = stadium.pk
        ser = StadiumSeatSerializer(instance=seat, data=data)
        ser.is_valid(raise_exception=True)
        seat = ser.save()
        resp = {
            "data": StadiumSeatSerializer(seat).data,
            "message": "Created Successfully",
            "status": status.HTTP_202_ACCEPTED
        }
        return Response(resp)

    def partial_update(self, request, stadium, pk):
        stadium = get_object_or_404(Stadium, id=stadium)
        seat = get_object_or_404(StadiumSeats, pk=pk, stadium=stadium)
        data = request.data
        data['stadium'] = stadium.pk
        ser = StadiumSeatSerializer(instance=seat, data=data, partial=True)
        ser.is_valid(raise_exception=True)
        seat = ser.save()
        resp = {
            "data": StadiumSeatSerializer(seat).data,
            "message": "Created Successfully",
            "status": status.HTTP_202_ACCEPTED
        }
        return Response(resp)

    def destroy(self, request, stadium, pk):
        stadium = get_object_or_404(Stadium, id=stadium)
        seat = get_object_or_404(StadiumSeats, pk=pk, stadium=stadium)
        try:
            seat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except django.db.OperationalError:
            return Response({
                'message': 'Tickets sold for this seat',
                'status': 400
            }, status=status.HTTP_400_BAD_REQUEST)
