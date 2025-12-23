from django.contrib.auth import authenticate
from ninja import Router
from ninja.errors import HttpError

from ..jwt import build_jwt_for_user
from ..models import User
from ..schemas import LoginRequest, TokenResponse

router = Router()


@router.post('/login', response=TokenResponse, auth=None)
def login(request, payload: LoginRequest):
    """User login endpoint - returns JWT token for valid credentials."""
    user = authenticate(request, email=payload.email, password=payload.password)

    if user is None:
        raise HttpError(400, 'Invalid credentials')

    if user.status != User.STATUS_ACTIVE:
        raise HttpError(403, 'User not active')

    token, expires_in = build_jwt_for_user(user)

    return TokenResponse(access_token=token, token_type='Bearer', expires_in=expires_in)
