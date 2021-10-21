import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from TicketReservation import settings
from stadiums.serializers import StadiumSerializer
from .models import Season, Team, Match, MatchSeats, League
from stadiums.models import StadiumSeats, Stadium


class SeasonSerializer(serializers.ModelSerializer):
    """
        Serializer for Seasons model,
        Seasons start date and end date must not over lap
    """
    class Meta:
        model = Season
        fields = '__all__'

    def validate(self, attrs):
        start_date = attrs['start_date']
        end_date = attrs['end_date']
        if start_date >= end_date:
            raise serializers.ValidationError({'end_date': 'End data must be greater than start date'})
        return attrs

    def create(self, validated_data):
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        qs = Season.objects.filter(
            Q(start_date__range=[start_date, end_date]) | Q(end_date__range=[start_date, end_date]) | Q(
                start_date__lte=start_date, end_date__gte=end_date)).exists()
        if qs:
            raise serializers.ValidationError({'general': 'A season is defined in this range'})
        return super(SeasonSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        qs = Season.objects.filter(
            Q(start_date__range=[start_date, end_date]) | Q(end_date__range=[start_date, end_date]) | Q(
                start_date__lte=start_date, end_date__gte=end_date)).exclude(id=instance.id).exists()
        if qs:
            raise serializers.ValidationError({'general': 'A season is defined in this range'})
        return super(SeasonSerializer, self).update(instance, validated_data)


class LeagueSerializer(serializers.ModelSerializer):
    """
        Serializer for League model
    """
    class Meta:
        model = League
        fields = '__all__'


class TeamsListSerializer(serializers.ModelSerializer):
    """
        Serializer for Team model as List
    """
    league = LeagueSerializer()

    class Meta:
        model = Team
        fields = '__all__'


class TeamsCreateSerializer(serializers.ModelSerializer):
    """
           Serializer for Team model
   """
    class Meta:
        model = Team
        fields = '__all__'


class MatchListSerializer(serializers.ModelSerializer):
    """
       Serializer for Match model as List
   """
    stadium_detail = serializers.SerializerMethodField(method_name='get_stadium')
    season = SeasonSerializer()
    host = TeamsListSerializer()
    guest = TeamsListSerializer()

    class Meta:
        model = Match
        exclude = ['stadium']

    def get_stadium(self, obj):
        return StadiumSerializer(Stadium.objects.get(id=obj.stadium)).data


class MatchCreateSerializer(serializers.ModelSerializer):
    """
        Serializer for Match model create
        :param: ticket_price, sets the ticket price globally for each seat, and creates the seats for the stadium
        :param: host_left, decides that host seats should be on left of stadium or right of it

   """
    ticket_price = serializers.IntegerField(validators=[MinValueValidator(0)], required=False)
    host_left = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = Match
        fields = '__all__'

    def validate(self, attrs):
        match_date = attrs.get('match_date')
        ticket_close_time = attrs.get('ticket_close_time')
        if match_date:
            match_date = match_date.replace(tzinfo=None)
            if match_date < datetime.datetime.now():
                raise serializers.ValidationError({'match_date': 'Match day cannot be before today'})
        if ticket_close_time:
            ticket_close_time = ticket_close_time.replace(tzinfo=None)
            if ticket_close_time > match_date:
                raise serializers.ValidationError(
                    {'ticket_close_time': 'Ticket Sales cannot happen after match begins'})

        host = attrs.get('host')
        guest = attrs.get('guest')
        if host and guest and host.pk == guest.pk:
            raise serializers.ValidationError({'host': 'host and guest cannot be same'})
        season = attrs.get('season')
        if season and season.end_date < datetime.date.today():
            raise serializers.ValidationError({'season': 'Select current season'})
        if not season.start_date <= match_date.date() <= season.end_date:
            raise serializers.ValidationError({'match_date': 'Match day must be between seasons'})
        stadium = attrs.get('stadium')
        if stadium:
            try:
                Stadium.objects.get(id=stadium)
            except ObjectDoesNotExist:
                raise serializers.ValidationError({'stadium': 'Please select a valid stadium'})
        return attrs

    def create(self, validated_data):
        ticket_price = validated_data.pop('ticket_price', None)
        host_left = validated_data.pop('host_left', True)

        match_date = validated_data.get('match_date')
        stadium = validated_data.get('stadium')
        before = match_date - datetime.timedelta(hours=settings.MATCH_DIFFERENCE_TIME)
        after = match_date + datetime.timedelta(hours=settings.MATCH_DIFFERENCE_TIME)
        qs = Match.objects.filter(match_date__range=[before, after], stadium=stadium).exists()
        if qs:
            raise serializers.ValidationError(
                {'match_date': ['There is another match for this time period in the current stadium']})
        instance = super(MatchCreateSerializer, self).create(validated_data)

        if ticket_price is not None:
            qs = StadiumSeats.objects.filter(stadium__id=instance.stadium).order_by('x_coordinate')
            min_x = qs.first().x_coordinate
            max_x = qs.last().x_coordinate
            length_stadium = max_x - min_x
            length_stadium = length_stadium * instance.share / 100
            if host_left:
                pivot = min_x + length_stadium
            else:
                host_left = False
                pivot = max_x - length_stadium
            seats_data = list()
            for seat in qs:
                is_host = host_left if seat.x_coordinate <= pivot else not host_left
                seats_data.append(
                    MatchSeats(match_id=instance.id, is_host=is_host, ticket_price=ticket_price, seat=seat.id)
                )
            MatchSeats.objects.bulk_create(seats_data)
        return instance

    def update(self, instance, validated_data):
        ticket_price = validated_data.pop('ticket_price', None)
        host_left = validated_data.pop('host_left', True)
        match_date = validated_data.get('match_date', instance.match_date)
        stadium = validated_data.get('stadium')
        before = match_date - datetime.timedelta(hours=settings.MATCH_DIFFERENCE_TIME)
        after = match_date + datetime.timedelta(hours=settings.MATCH_DIFFERENCE_TIME)
        qs = Match.objects.filter(match_date__range=[before, after], stadium=stadium).exclude(id=instance.id).exists()
        if qs:
            raise serializers.ValidationError(
                {'match_date': ['There is another match for this time period in the current stadium']})
        instance = super(MatchCreateSerializer, self).update(instance, validated_data)
        if ticket_price is not None:
            seats = MatchSeats.objects.filter(match=instance)
            if seats:
                seats.update(ticket_price=ticket_price)
            else:
                qs = StadiumSeats.objects.filter(stadium__id=instance.stadium).order_by('x_coordinate')
                min_x = qs.first().x_coordinate
                max_x = qs.last().x_coordinate
                length_stadium = max_x - min_x
                length_stadium = length_stadium * instance.share / 100
                if host_left:
                    pivot = min_x + length_stadium
                else:
                    host_left = False
                    pivot = max_x - length_stadium
                seats_data = list()
                for seat in qs:
                    is_host = host_left if seat.x_coordinate <= pivot else not host_left
                    seats_data.append(
                        MatchSeats(match_id=instance.id, is_host=is_host, ticket_price=ticket_price, seat=seat.id)
                    )
                MatchSeats.objects.bulk_create(seats_data)
        return instance


class MatchSeatsSerializer(serializers.ModelSerializer):
    """
        Serializer for MatchSeats model
    """
    class Meta:
        model = MatchSeats
        fields = '__all__'

    def validate(self, attrs):
        seat = attrs.get('seat', None)
        if seat:
            try:
                StadiumSeats.objects.get(pk=seat)
            except ObjectDoesNotExist:
                raise serializers.ValidationError({'seat': ['No Such Seat']})
        return attrs


class RowMatchSeatSerializer(serializers.Serializer):
    """
        Serializer for MatchSeats model with the option of creating tickets for rows of seats
        :param: rows, list of rows set
        :param: ticket_price, ticket price for selected rows
        :param: match, the match that seats are assigned to
        :param: host_left, decides that host seats should be on left of stadium or right of it
    """
    rows = serializers.ListField(child=serializers.IntegerField(validators=[MinValueValidator(1)]))
    ticket_price = serializers.IntegerField(validators=[MinValueValidator(0)])
    match = serializers.PrimaryKeyRelatedField(queryset=Match.objects.all())
    host_left = serializers.BooleanField(default=True, required=False)

    def create(self, validated_data):
        rows = validated_data.get('rows')
        ticket_price = validated_data.get('ticket_price')
        match = validated_data.get('match')
        stadium = match.stadium
        qs = StadiumSeats.objects.filter(stadium__id=stadium, row__in=rows).order_by('x_coordinate')
        if not qs:
            raise serializers.ValidationError({'seat': 'No seat is defined'})
        min_x = qs.first().x_coordinate
        max_x = qs.last().x_coordinate
        length_stadium = max_x - min_x
        length_stadium = length_stadium * match.share / 100
        host_left = validated_data.get('host_left', True)
        if host_left:
            pivot = min_x + length_stadium
        else:
            host_left = False
            pivot = max_x - length_stadium
        seats_data = list()
        for seat in qs:
            is_host = host_left if seat.x_coordinate <= pivot else not host_left
            seats_data.append(
                MatchSeats(match=match, is_host=is_host, ticket_price=ticket_price, seat=seat.id)
            )
        try:
            MatchSeats.objects.bulk_create(seats_data)
        except:
            raise serializers.ValidationError({'general': 'Seat is already defined'})
        return MatchSeats()

    def update(self, instance, validated_data):
        rows = validated_data.get('rows')
        ticket_price = validated_data.get('ticket_price')
        match = validated_data.get('match')
        stadium = match.stadium
        qs = StadiumSeats.objects.filter(stadium__id=stadium, row__in=rows).order_by('x_coordinate')
        if not qs:
            raise serializers.ValidationError({'seat': 'No seat is defined'})
        seats = set([seat.id for seat in qs])
        MatchSeats.objects.filter(seat__in=seats, match=match).update(ticket_price=ticket_price)
        return None
