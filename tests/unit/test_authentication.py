import time
import uuid

import jwt
import pytest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

from src.user.authentication import JWTUserAuthentication, ServiceAuthentication
from src.user.models import Service, User

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


def test_jwt_user_authentication_returns_none_without_bearer_header():
    request = APIRequestFactory().get('/')

    result = JWTUserAuthentication().authenticate(request)

    assert result is None


def test_jwt_user_authentication_rejects_expired_token(settings, regular_user: User):
    now = int(time.time())
    token = jwt.encode(
        {
            'sub': str(regular_user.id),
            'email': regular_user.email,
            'iat': now - 10,
            'exp': now - 1,
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    request = APIRequestFactory().get('/', HTTP_AUTHORIZATION=f'Bearer {token}')

    with pytest.raises(AuthenticationFailed, match='Token has expired'):
        JWTUserAuthentication().authenticate(request)


def test_jwt_user_authentication_rejects_invalid_token():
    request = APIRequestFactory().get('/', HTTP_AUTHORIZATION='Bearer not-a-jwt')

    with pytest.raises(AuthenticationFailed, match='Invalid token'):
        JWTUserAuthentication().authenticate(request)


def test_jwt_user_authentication_rejects_missing_sub(settings, regular_user: User):
    now = int(time.time())
    token = jwt.encode(
        {
            'email': regular_user.email,
            'iat': now,
            'exp': now + 60,
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    request = APIRequestFactory().get('/', HTTP_AUTHORIZATION=f'Bearer {token}')

    with pytest.raises(AuthenticationFailed, match='Token missing user ID'):
        JWTUserAuthentication().authenticate(request)


def test_jwt_user_authentication_rejects_unknown_user(settings):
    now = int(time.time())
    token = jwt.encode(
        {
            'sub': str(uuid.uuid4()),
            'email': 'missing@example.com',
            'iat': now,
            'exp': now + 60,
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    request = APIRequestFactory().get('/', HTTP_AUTHORIZATION=f'Bearer {token}')

    with pytest.raises(AuthenticationFailed, match='User not found'):
        JWTUserAuthentication().authenticate(request)


def test_jwt_user_authentication_rejects_inactive_user(settings, regular_user: User):
    regular_user.status = User.STATUS_INACTIVE
    regular_user.save(update_fields=['status'])

    now = int(time.time())
    token = jwt.encode(
        {
            'sub': str(regular_user.id),
            'email': regular_user.email,
            'iat': now,
            'exp': now + 60,
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    request = APIRequestFactory().get('/', HTTP_AUTHORIZATION=f'Bearer {token}')

    with pytest.raises(AuthenticationFailed, match='User account is not active'):
        JWTUserAuthentication().authenticate(request)


def test_service_authentication_returns_none_when_headers_missing():
    request = APIRequestFactory().get('/')

    result = ServiceAuthentication().authenticate(request)

    assert result is None


def test_service_authentication_accepts_valid_credentials(service: Service):
    request = APIRequestFactory().get(
        '/',
        HTTP_X_CLIENT_ID=service.client_id,
        HTTP_X_CLIENT_SECRET=service.client_secret,
    )

    user_auth_tuple = ServiceAuthentication().authenticate(request)

    assert user_auth_tuple is not None
    user, authed_service = user_auth_tuple
    assert user is None
    assert authed_service.id == service.id
    assert request.service.id == service.id


def test_service_authentication_rejects_invalid_credentials(service: Service):
    request = APIRequestFactory().get(
        '/',
        HTTP_X_CLIENT_ID=service.client_id,
        HTTP_X_CLIENT_SECRET='wrong',
    )

    with pytest.raises(AuthenticationFailed, match='Invalid client credentials'):
        ServiceAuthentication().authenticate(request)


def test_service_authentication_rejects_inactive_service(service: Service):
    service.status = 'INACTIVE'
    service.save(update_fields=['status'])

    request = APIRequestFactory().get(
        '/',
        HTTP_X_CLIENT_ID=service.client_id,
        HTTP_X_CLIENT_SECRET=service.client_secret,
    )

    with pytest.raises(AuthenticationFailed, match='Service is not active'):
        ServiceAuthentication().authenticate(request)
