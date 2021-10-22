from django.urls import path
from .views import TicketsView, ConfirmPaymentView

urlpatterns = [
    path('payment/<int:ticket_id>/', ConfirmPaymentView.as_view()),
    path('<int:ticket_id>/', TicketsView.as_view()),
    path('', TicketsView.as_view()),
]
