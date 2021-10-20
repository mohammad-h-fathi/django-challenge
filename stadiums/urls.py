from django.urls import path, include
from .views import StadiumsViewSet, StadiumSeatsView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', StadiumsViewSet, basename='seats')

router_seats = DefaultRouter()
router_seats.register(r'', StadiumSeatsView, basename='seats')

urlpatterns = [

    # STADIUMS
    path('', include(router.urls)),
    path('seats/<int:stadium>/', include(router_seats.urls)),
    # path('stadium/matches/<int:pk>', StadiumDeleteView.as_view()),



]

