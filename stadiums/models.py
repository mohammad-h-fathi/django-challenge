import django.db
from django.core.validators import MinValueValidator
from django.db import models


from tickets.models import Ticket
from matches.models import MatchSeats
# Create your models here.


class Stadium(models.Model):
    """
            name: name of the stadium
            address: address of the stadium
            province: the province stadium resides in
            city: the city stadium resides in
            capacity: capacity of the  stadium
        """
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    capacity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)


class StadiumSeats(models.Model):
    """
        seat_no: number of the seat
        row: the row of seat in stadium
        column: the column of seat in stadium
        x_coordinate: the `x` coordinate of the seat
        y_coordinate: the `y` coordinate of the seat
        stadium: the stadium which seat is defined for
    """
    id = models.BigAutoField(primary_key=True)
    seat_no = models.IntegerField(validators=[MinValueValidator(1)])
    row = models.IntegerField(default=0, validators=[MinValueValidator(1)])
    column = models.IntegerField(default=0, validators=[MinValueValidator(1)])
    x_coordinate = models.FloatField(default=0)
    y_coordinate = models.FloatField(default=0)
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)

    class Meta:
        unique_together = [('row', 'column', 'stadium', 'seat_no'),
                           ('x_coordinate', 'y_coordinate', 'stadium')]

    def delete(self, using=None, keep_parents=False):
        match_seats = MatchSeats.objects.filter(seat=self.id)
        if not match_seats:
            return super(StadiumSeats, self).delete(using, keep_parents)
        ms_list = [ms.id for ms in match_seats]
        tickets = Ticket.objects.filter(match_seats__in=ms_list).exists()
        if not tickets:
            for ms in match_seats:
                ms.delete()
            return super(StadiumSeats, self).delete(using, keep_parents)
        raise django.db.OperationalError()
