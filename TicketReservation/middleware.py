import datetime
import os
import json
import jwt

from base64 import b64encode, b64decode
from types import SimpleNamespace

from django.contrib.auth.models import Permission, Group
from django.http import JsonResponse
from rest_framework import status, exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.response import Response

from users.models import User
from users.serializers import UserTokenSerializer
from .aes import AES

AES_KEY = bytes(os.getenv('AES_KEY').encode('utf-8'))
AES_IV = bytes(os.getenv('AES_IV').encode('utf-8'))
TOKEN_TTL = int(os.getenv('TOKEN_TTL'))
JWT_KEY = os.getenv('JWT_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')


def create_token(user_data):
    final_user_data = json.dumps(user_data)
    ct = AES(AES_KEY).encrypt_ctr(bytes(str(final_user_data).encode()), AES_IV)
    ct = b64encode(ct).decode('utf-8')
    payload = {
        'data': ct,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=TOKEN_TTL)
    }
    token = jwt.encode(payload, JWT_KEY, JWT_ALGORITHM)
    return token


def decode_token(auth):
    if auth:
        auth = auth.strip()
        auth = auth.split(' ')[-1]
        jwt_token = auth
        payload = jwt.decode(jwt_token, JWT_KEY,
                             algorithms=[JWT_ALGORITHM])
        data = b64decode(payload['data'])
        dt = AES(AES_KEY).decrypt_ctr(data, AES_IV)
        final_data = json.loads(dt)
        groups = final_data.pop('groups', None)
        user_permissions = final_data.pop('user_permissions', None)
        user = User(**final_data)
        user.user_permissions_set = [Permission(**g) for g in user_permissions]
        user.groups_set = [Group(**g) for g in groups]
        return user
    return None


class MyTokenAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def enforce_csrf(self, request):
        return

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)
        try:
            user_data = decode_token(token)
            return (user_data, None)
        except jwt.exceptions.InvalidSignatureError:
            msg = "Invalid Signature Error"
        except jwt.exceptions.ExpiredSignatureError:
            msg = 'Signature is Expired'
        except Exception as e:
            msg = 'Invalid Token'
        raise exceptions.AuthenticationFailed(msg)
