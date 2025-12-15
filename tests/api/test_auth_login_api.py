import pytest

from src.user.jwt import decode_jwt
from src.user.models import User

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_login_returns_jwt_for_active_user(api_client, regular_user: User):
    response = api_client.post(
        '/api/auth/login',
        {'email': regular_user.email, 'password': 'password123'},
        format='json',
    )

    assert response.status_code == 200
    assert response.data['token_type'] == 'Bearer'
    assert response.data['expires_in'] == 3600

    payload = decode_jwt(response.data['access_token'])
    assert payload['email'] == regular_user.email
    assert payload['sub'] == str(regular_user.id)


def test_login_rejects_invalid_credentials(api_client, regular_user: User):
    response = api_client.post(
        '/api/auth/login',
        {'email': regular_user.email, 'password': 'wrong'},
        format='json',
    )

    assert response.status_code == 400
    assert response.data['detail'] == 'Invalid credentials'


def test_login_rejects_inactive_user(api_client, regular_user: User):
    regular_user.status = User.STATUS_INACTIVE
    regular_user.save(update_fields=['status'])

    response = api_client.post(
        '/api/auth/login',
        {'email': regular_user.email, 'password': 'password123'},
        format='json',
    )

    assert response.status_code == 403
    assert response.data['detail'] == 'User not active'
