import time

import jwt
import pytest

from src.user.jwt import build_jwt_for_user, decode_jwt
from src.user.models import (
    Permission,
    RolePermission,
    User,
    UserGlobalPermission,
    UserGlobalRole,
    UserServiceAssignment,
    UserServicePermission,
    UserServiceRole,
)

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


def test_build_jwt_for_user_includes_global_and_service_claims(
    regular_user: User,
    service,
    global_permission: Permission,
    global_role,
    service_permission: Permission,
    service_role,
):
    UserGlobalPermission.objects.create(user=regular_user, permission=global_permission)

    UserGlobalRole.objects.create(user=regular_user, role=global_role)
    RolePermission.objects.create(role=global_role, permission=global_permission)

    UserServiceAssignment.objects.create(user=regular_user, service=service, created_by=None)
    UserServicePermission.objects.create(
        user=regular_user, service=service, permission=service_permission
    )

    UserServiceRole.objects.create(user=regular_user, service=service, role=service_role)
    RolePermission.objects.create(role=service_role, permission=service_permission)

    token, expires_in = build_jwt_for_user(regular_user)

    assert isinstance(token, str)
    assert expires_in == 3600

    payload = decode_jwt(token)

    assert payload['sub'] == str(regular_user.id)
    assert payload['email'] == regular_user.email
    assert set(payload['global_permissions']) == {'admin'}
    assert payload['global_roles'] == ['super_admin']

    service_id = str(service.id)
    assert service_id in payload['services']
    assert set(payload['services'][service_id]['permissions']) == {'read'}
    assert payload['services'][service_id]['roles'] == ['editor']


def test_decode_jwt_rejects_invalid_signature(settings, regular_user: User):
    now = int(time.time())
    payload = {
        'sub': str(regular_user.id),
        'email': regular_user.email,
        'iat': now,
        'exp': now + 60,
    }

    wrong_secret_token = jwt.encode(payload, 'wrong-secret', algorithm=settings.JWT_ALGORITHM)

    with pytest.raises(jwt.InvalidTokenError):
        decode_jwt(wrong_secret_token)
