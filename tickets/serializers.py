from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from stadiums.models import StadiumSeats
from matches.models import MatchSeats
from matches.serializers import MatchListSerializer

from .models import Ticket


class TicketListSerializer(serializers.ModelSerializer):

    ticket_info = serializers.SerializerMethodField()

    def get_ticket_info(self, obj):
        data = None
        try:
            ms = MatchSeats.objects.get(id=obj.match_seat)
            ss = StadiumSeats.objects.get(id=ms.seat)
            data = {
                'row': ss.row,
                'column': ss.column,
                'price': ms.ticket_price,
                'match': MatchListSerializer(ms.match).data
            }
        except ObjectDoesNotExist:
            pass
        return data

    class Meta:
        model = Ticket
        exclude = ['match_seat', 'user']

#
# class TicketCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ticket
#         exclude = ['submit_date', 'status']
#
#     def validate(self, attrs):
#


