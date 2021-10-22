from django.db import models


# Create your models here.


class Ticket(models.Model):
    id = models.BigAutoField(primary_key=True)
    match_seat = models.BigIntegerField(default=0, null=False, blank=False, unique=True,
                                        error_messages={'match_seat': 'This Seat is already sold'})
    user = models.IntegerField()
    status = models.SmallIntegerField(default=1)
    submit_date = models.DateTimeField(auto_now_add=True)

