from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        instance, _ = User.objects.get_or_create(username=validated_data['username'])
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.CharField(max_length=150, required=False)
    province = serializers.CharField(max_length=100, required=False)
    national_code = serializers.CharField(max_length=10, required=False)
    mobile_number = serializers.CharField(max_length=11, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'province', 'city', 'national_code', 'mobile_number']


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'is_active']


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'is_active']
