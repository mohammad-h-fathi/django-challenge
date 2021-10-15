from django.db import models

# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)


class Stadium(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    capacity = models.IntegerField(default=0)


class StadiumSeats(models.Model):
    seat_no = models.IntegerField()
    is_host = models.BooleanField(default=True)
    row = models.FloatField(default=0)
    column = models.FloatField(default=0)
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)


class Match(models.Model):
    match_date = models.DateTimeField()
    ticket_close_time = models.DateTimeField()
    host = models.ForeignKey(Team, on_delete=models.RESTRICT, related_name="match_host")
    guest = models.ForeignKey(Team, on_delete=models.RESTRICT, related_name="match_guest")
    stadium = models.ForeignKey(Stadium, on_delete=models.RESTRICT)


class MatchSeats(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    seat = models.ForeignKey(StadiumSeats, on_delete=models.CASCADE)
    ticket_price = models.BigIntegerField()


class Ticket(models.Model):
    match_seat = models.ForeignKey(MatchSeats, on_delete=models.RESTRICT)
    user = models.IntegerField()
    status = models.SmallIntegerField(default=1)
    submit_date = models.DateTimeField(auto_now_add=True)

