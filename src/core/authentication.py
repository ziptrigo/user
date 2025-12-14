import jwt
from rest_framework import authentication, exceptions

from src.accounts.models import Service, User
from src.core.jwt import decode_jwt


class JWTUserAuthentication(authentication.BaseAuthentication):
    """
    JWT-based authentication for users.

    Expects Authorization header: Bearer <token>
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]  # Remove 'Bearer ' prefix

        try:
            payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

        user_id = payload.get('sub')
        if not user_id:
            raise exceptions.AuthenticationFailed('Token missing user ID')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        if user.status != User.STATUS_ACTIVE:
            raise exceptions.AuthenticationFailed('User account is not active')

        return (user, payload)


class ServiceAuthentication(authentication.BaseAuthentication):
    """
    Service authentication using client_id and client_secret.

    Expects headers:
    - X-Client-Id: <client_id>
    - X-Client-Secret: <client_secret>
    """

    def authenticate(self, request):
        client_id = request.META.get('HTTP_X_CLIENT_ID')
        client_secret = request.META.get('HTTP_X_CLIENT_SECRET')

        if not client_id or not client_secret:
            return None

        try:
            service = Service.objects.get(client_id=client_id)
        except Service.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid client credentials')

        if service.client_secret != client_secret:
            raise exceptions.AuthenticationFailed('Invalid client credentials')

        if service.status != 'ACTIVE':
            raise exceptions.AuthenticationFailed('Service is not active')

        # Attach service to request for later use
        request.service = service

        return (None, service)
