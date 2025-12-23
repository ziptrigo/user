import uuid

import pytest

from tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _jwt_settings(settings):
    """Make JWT behavior deterministic for tests."""
    settings.JWT_SECRET = 'test-secret'
    settings.JWT_ALGORITHM = 'HS256'
    settings.JWT_EXP_DELTA_SECONDS = 3600


@pytest.fixture()
def api_client():
    from ninja.testing import TestClient

    from src.user.api import api

    return TestClient(api)


@pytest.fixture()
def admin_user():
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture()
def regular_user():
    return UserFactory()


@pytest.fixture()
def service():
    from src.user.models import Service

    return Service.objects.create(
        name=f'service-{uuid.uuid4().hex}',
        description='Test service',
        client_id=f'client-{uuid.uuid4().hex}',
        client_secret=f'secret-{uuid.uuid4().hex}',
        status='ACTIVE',
    )


@pytest.fixture()
def service_permission(service):
    from src.user.models import Permission

    return Permission.objects.create(
        type=Permission.TYPE_SERVICE,
        service=service,
        code='read',
        description='Read permission',
    )


@pytest.fixture()
def global_permission():
    from src.user.models import Permission

    return Permission.objects.create(
        type=Permission.TYPE_GLOBAL,
        service=None,
        code='admin',
        description='Admin permission',
    )


@pytest.fixture()
def service_role(service):
    from src.user.models import Role

    return Role.objects.create(service=service, name='editor', description='Editor role')


@pytest.fixture()
def global_role():
    from src.user.models import Role

    return Role.objects.create(service=None, name='super_admin', description='Global super admin')
