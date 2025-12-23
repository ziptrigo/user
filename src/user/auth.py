import jwt
from ninja.security import HttpBearer

from .jwt import decode_jwt
from .models import User


class JWTAuth(HttpBearer):
    """JWT-based authentication for users using Django Ninja's HttpBearer."""

    def authenticate(self, request, token: str):
        try:
            payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

        user_id = payload.get('sub')
        if not user_id:
            return None

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

        if user.status != User.STATUS_ACTIVE:
            return None

        return user


class AdminAuth(JWTAuth):
    """JWT authentication that also requires admin (staff) privileges."""

    def authenticate(self, request, token: str):
        user = super().authenticate(request, token)
        
        if user is None:
            return None
        
        if not user.is_staff:
            return None
        
        return user
