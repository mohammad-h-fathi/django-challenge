from django.contrib import admin

# Register your models here.
from .models import Season, Team, Match, MatchSeats, League

admin.site.register(Season)
admin.site.register(League)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(MatchSeats)
