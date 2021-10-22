import datetime
import copy

import django.db.utils
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status, views, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from stadiums.models import Stadium

from matches.models import Match, MatchSeats

from .serializers import TicketListSerializer
from .models import Ticket


class TicketsView(views.APIView):

    def get_filtered_response(self):
        """
            filters and paginates the request from user by query parameters
        :return: paginated response of tickets list for the current user
        """
        query_params = copy.copy(self.request.query_params)
        tickets_qs = Ticket.objects.filter(user=self.request.user.id)
        query_params.pop('page', 1)
        if query_params:
            seats = MatchSeats.objects.filter(id__in=[ticket.match_seat for ticket in tickets_qs]) \
                .values_list('match_id', flat=True).distinct()
            match_qs = Match.objects.filter(id__in=seats)
            has_query = False
            if query_params.get('stadium', None):
                stadiums_qs = Stadium.objects.filter(name__icontains=query_params.get('stadium', None)).distinct()
                match_qs = match_qs.filter(stadium__in=[std.id for std in stadiums_qs])
                has_query = True

            if query_params.get('team', None):
                match_qs = match_qs.filter(Q(host__name__icontains=query_params.get('team', None)) | Q(
                    guest__name__icontains=query_params.get('team', None)))
                has_query = True

            if query_params.get('match_date', None):
                match_qs = match_qs.filter(match_date__icontains=query_params.get('match_date', None))
                has_query = True

            elif query_params.get('match_date_after', None):
                match_qs = match_qs.filter(match_date__gte=query_params.get('match_date_after', None))
                has_query = True

            elif query_params.get('match_date_before', None):
                match_qs = match_qs.filter(match_date__lte=query_params.get('match_date_before', None))
                has_query = True

            if has_query:
                match_qs = match_qs.values_list('id', flat=True)
                seats = MatchSeats.objects.filter(id__in=[ticket.match_seat for ticket in tickets_qs],
                                                  match__id__in=match_qs).values_list('id', flat=True)
                tickets_qs = tickets_qs.filter(match_seat__in=[seat for seat in seats])
        tickets_qs = tickets_qs.order_by('submit_date').reverse()
        paginator = PageNumberPagination()
        paginator.page_query_param = 'page'
        paginator.page_size = 50
        paginated_qs = paginator.paginate_queryset(tickets_qs, self.request)
        ser_data = TicketListSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(ser_data.data)

    def get(self, request, ticket_id=None):
        if ticket_id:
            instance = get_object_or_404(Ticket, id=ticket_id, user=self.request.user.id)
            return Response(TicketListSerializer(instance).data)
        else:
            return self.get_filtered_response()

    def validate_user_already_bought_ticket(self, match):
        """
            This function validates that user have already bought a ticket for current match or not,
            :param match: current match
            :raises validation error for bought ticket
            :return: None
        """
        match_seats = MatchSeats.objects.filter(match=match).values_list('id', flat=True)
        tickets = Ticket.objects.filter(user=self.request.user.id, match_seat__in=[ms for ms in match_seats])
        if tickets:
            raise ValidationError({'general': 'You already have bought a ticket for this match'})

    def validate_seat(self):
        """
            This function validates the post data:
            1 - if selected seat is valid,
            2 - ticket sell time is not over
            3 - selected team is valid for match
            4 - selected seat section (host/guest) is corresponding to selected team
        :return: match_seat object
        """
        data = self.request.data
        try:
            ms = MatchSeats.objects.get(id=data.get('match_seat', 0))
            if ms.match.ticket_close_time.replace(tzinfo=None) < datetime.datetime.utcnow():
                raise ValidationError({'general': 'Tickets sell time is over'})
        except ObjectDoesNotExist:
            raise ValidationError({'match_seat': 'Invalid seat selected'})
        team = data.get('team', None)
        if not team:
            raise ValidationError({'team': 'Please select your team'})
        if ms.match.host_id == team:
            if not ms.is_host:
                raise ValidationError({'match_seat': 'Please select a seat in hosts section'})
        elif ms.match.guest_id == team:
            if ms.is_host:
                raise ValidationError({'match_seat': 'Please select a seat in guests section'})
        else:
            raise ValidationError({'team': 'Please select a team corresponding to current match'})
        return ms

    def post(self, request):
        ms = self.validate_seat()
        self.validate_user_already_bought_ticket(ms.match)
        ticket = Ticket(match_seat=ms.id, user=request.user.id)
        try:
            ticket.save()
            return Response(TicketListSerializer(ticket).data, status=status.HTTP_201_CREATED)
        except django.db.utils.IntegrityError:
            return Response(
                {'message': {'match_seat': 'This seat is already taken'}, 'status': 400},
                status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, ticket_id):
        """
            Updated Ticket Location
            if ticket prices are different, and additional payment is required, its status is changed
        :param request:
        :param ticket_id:
        :return:
        """
        try:
            ms = self.validate_seat()
            ticket = Ticket.objects.get(id=ticket_id, user=request.user.id)
            if ticket.match_seat == ms.id:
                return Response(
                    {'message': {'match_seat': 'If you want to change your seat, dont choose same one'}, 'status': 400},
                    status=status.HTTP_400_BAD_REQUEST)
            ticket.match_seat = ms.id
            if ms.ticket_price > MatchSeats.objects.get(id=ticket.match_seat).ticket_price:
                ticket.status = 1
            ticket.save()
            return Response(TicketListSerializer(ticket).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'message': 'not found', 'status': 404}, status=status.HTTP_404_NOT_FOUND)
        except django.db.utils.IntegrityError:
            return Response(
                {'message': {'match_seat': 'This seat is already taken'}, 'status': 400},
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id, user=request.user.id)
            if ticket.status == 2:
                return Response({'message': 'Cannot cancel paid ticket', 'status': 400},
                                status=status.HTTP_400_BAD_REQUEST)
            ticket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'message': 'not found', 'status': 404}, status=status.HTTP_404_NOT_FOUND)


class ConfirmPaymentView(views.APIView):
    """
        Its is considered that this request is coming from PGW
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if ticket.status != 2:
            ticket.status = 2
            ticket.save()
        return Response(TicketListSerializer(ticket).data, status=status.HTTP_201_CREATED)
