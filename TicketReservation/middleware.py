import datetime
import os
import json
import jwt

from base64 import b64encode, b64decode
from types import SimpleNamespace

from django.contrib.auth.models import Permission, Group
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from users.models import User
from users.serializers import UserTokenSerializer
from .aes import AES

AES_KEY = bytes(os.getenv('AES_KEY').encode('utf-8'))
AES_IV = bytes(os.getenv('AES_IV').encode('utf-8'))
TOKEN_TTL = int(os.getenv('TOKEN_TTL'))
JWT_KEY = os.getenv('JWT_KEY').replace('\\n', '\n').strip().replace('"', '')
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


def auth_middleware(get_response):
    def middleware(request):
        auth = request.headers.get('Authorization', None)
        if auth:
            try:
                user_data = decode_token(auth)
            except jwt.exceptions.InvalidSignatureError:
                return JsonResponse({'data': None,
                                     'status': 401,
                                     'message': "Invalid Signature Error"}
                                    , status=status.HTTP_401_UNAUTHORIZED)
            except jwt.exceptions.ExpiredSignatureError:
                return JsonResponse({
                    'data': None,
                    'status': 401,
                    'message': 'Signature is Expired'},
                    status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                print(e)
                return JsonResponse({'data': None,
                                     'status': 401,
                                     'message': 'Invalid Token'},
                                    status=status.HTTP_401_UNAUTHORIZED)
            request.user = user_data
        response = get_response(request)
        return response

    return middleware
