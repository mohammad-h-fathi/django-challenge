import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions, views
from rest_framework.response import Response

from TicketReservation.middleware import create_token
from .serializers import *

# Create your views here.


class UserRegistryView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        self.perform_create(ser)
        return Response({'data': None, 'status': 201, 'messages': {
            'general': 'User Created Successfully'
        }}, status=status.HTTP_201_CREATED)


class UserLoginView(views.APIView):

    def post(self, request):
        if request.user.is_authenticated:
            return Response(
                {
                    'data': UserInfoSerializer(self.request.user),
                    'status': 200,
                    'message': {
                        'general': 'You are already logged in'
                    }
                }
            )
        #
        try:
            instance = User.objects.get(username=self.request.data.get('username'), is_active=1)
        except ObjectDoesNotExist:
            return Response({
                'status': 400,
                'message': {
                    'general': 'Invalid username or password'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        if not instance.check_password(request.data.get('password')):
            return Response({
                'status': 400,
                'message': {
                    'general': 'Invalid username or password'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.last_login = datetime.datetime.utcnow()
        instance.save()
        user_info = UserInfoSerializer(instance).data

        user_info['token'] = create_token(UserTokenSerializer(instance).data)
        return Response({
            'data': user_info
        })


class UserInfoView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserInfoSerializer

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)
