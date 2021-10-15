from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

from .validators import national_code_validator, mobile_number_validator


# Create your models here.


class User(AbstractUser):
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, unique=True, error_messages={
        'unique': 'Email already taken'
    })
    balance = models.FloatField(default=0)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    national_code = models.CharField(max_length=10, validators=[national_code_validator, MinLengthValidator(10)],
                                     unique=True, blank=True, default=None, null=True,
                                     error_messages={
                                         'unique': "National Code already taken"
                                     })
    mobile_number = models.CharField(max_length=11, validators=[MinLengthValidator(10), mobile_number_validator],
                                     unique=True, blank=True, default=None, null=True,
                                     error_messages={
                                         'unique': "Mobile Number already taken"
                                     })
