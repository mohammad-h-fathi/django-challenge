from django.core.validators import MinValueValidator
from django.db import models
from rest_framework import serializers

from tickets.models import Ticket
# Create your models here.


class Season(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()


class League(models.Model):
    name = models.CharField(max_length=70, unique=True)
    rating = models.IntegerField(default=1)


class Team(models.Model):
    """
        name: name of the team
        province: the province team resides in
        city: the city team resides in
        league: the league the team is in
        is_active: team is active or not
    """
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    league = models.ForeignKey(League, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)


class Match(models.Model):
    """
        match_date: the date match is appointed to
        ticket_close_time: when ticket selling stop
        host : hosting team
        guest: guest team
        share: seats share percentage for the host, default is 80 for host and 20 for guest
        stadium: the stadium match happens in
    """
    id = models.BigAutoField(primary_key=True)
    match_date = models.DateTimeField()
    ticket_close_time = models.DateTimeField()
    share = models.IntegerField(default=80, null=False, blank=False)
    host = models.ForeignKey(Team, on_delete=models.DO_NOTHING, related_name='host_team')
    guest = models.ForeignKey(Team, on_delete=models.DO_NOTHING, related_name='guest_team')
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    stadium = models.IntegerField(default=0, null=False, blank=False)

    class Meta:
        unique_together = ['stadium', 'match_date']


class MatchSeats(models.Model):
    """
        defined seats for each match, with price of each seat
        match: the current match
        seat: the seat id of the stadium
        ticket_price: the ticket price for the seat
    """
    id = models.BigAutoField(primary_key=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    seat = models.BigIntegerField()
    is_host = models.BooleanField(default=True)
    ticket_price = models.BigIntegerField()

    class Meta:
        unique_together = ['seat', 'match']
        
    def delete(self, using=None, keep_parents=False):
        qs = Ticket.objects.filter(match_seat=self.id)
        if qs:
            raise serializers.ValidationError({'general': 'Seat is sold, cannot delete'})
        return super(MatchSeats, self).delete(using, keep_parents)
