import time
import uuid
from unittest.mock import Mock

import jwt
import pytest

from src.user.auth import AdminAuth, JWTAuth
from src.user.models import User

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


def test_jwt_auth_returns_none_without_valid_token():
    request = Mock()
    
    result = JWTAuth().authenticate(request, '')
    
    assert result is None


def test_jwt_auth_accepts_valid_token(settings, regular_user: User):
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
    
    request = Mock()
    result = JWTAuth().authenticate(request, token)
    
    assert result is not None
    assert result.id == regular_user.id


def test_jwt_auth_returns_none_for_expired_token(settings, regular_user: User):
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
    
    request = Mock()
    result = JWTAuth().authenticate(request, token)
    
    assert result is None


def test_jwt_auth_returns_none_for_invalid_token():
    request = Mock()
    
    result = JWTAuth().authenticate(request, 'not-a-jwt')
    
    assert result is None


def test_jwt_auth_returns_none_for_missing_sub(settings, regular_user: User):
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
    
    request = Mock()
    result = JWTAuth().authenticate(request, token)
    
    assert result is None


def test_jwt_auth_returns_none_for_unknown_user(settings):
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
    
    request = Mock()
    result = JWTAuth().authenticate(request, token)
    
    assert result is None


def test_jwt_auth_returns_none_for_inactive_user(settings, regular_user: User):
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
    
    request = Mock()
    result = JWTAuth().authenticate(request, token)
    
    assert result is None


def test_admin_auth_accepts_staff_user(settings, admin_user: User):
    now = int(time.time())
    token = jwt.encode(
        {
            'sub': str(admin_user.id),
            'email': admin_user.email,
            'iat': now,
            'exp': now + 60,
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    request = Mock()
    result = AdminAuth().authenticate(request, token)
    
    assert result is not None
    assert result.id == admin_user.id


def test_admin_auth_rejects_non_staff_user(settings, regular_user: User):
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
    
    request = Mock()
    result = AdminAuth().authenticate(request, token)
    
    assert result is None
