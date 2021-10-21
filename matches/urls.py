from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamsViewSet, SeasonViewSet, MatchesViewSet, LeagueViewSet, TeamMatchesGenericView, MatchSeatsViewSet

router = DefaultRouter()
router.register(r'teams', TeamsViewSet, basename='teams')
router.register(r'seasons', SeasonViewSet, basename='seasons')
router.register(r'matches', MatchesViewSet, basename='matches')
router.register(r'leagues', LeagueViewSet, basename='matches')

router_match_seats = DefaultRouter()
router_match_seats.register(r'', MatchSeatsViewSet, basename='match_seats')

urlpatterns = [

    # LIST OF TEAM MATCHES
    path('teams/matches/<int:team_id>/', TeamMatchesGenericView.as_view()),

    # MATCH SEATS
    path('matches/seats/<int:match_id>/', include(router_match_seats.urls)),

    # ALL ROUTERS
    path('', include(router.urls)),
]
