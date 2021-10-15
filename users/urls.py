from django.urls import path
from .views import UserRegistryView, UserInfoView, UserLoginView

urlpatterns = [
    path('register/', UserRegistryView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('info/', UserInfoView.as_view()),
]
