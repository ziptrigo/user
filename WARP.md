# User Service Project

## Project Overview
Centralized Single Sign-On (SSO) service for ZipTrigo applications. Provides JWT-based user authentication, service (machine-to-machine) authentication via client_id/client_secret, centralized users/roles/permissions, and a minimal HTMX landing page.

## Goals
- Single source of truth for identity, roles and permissions
- Issue JWTs that client apps can validate
- Provide a clean REST API under `/api`
- Manage service-level credentials for first-party apps

## Tech Stack
- Python 3.13
- Django 6.0 + Django Ninja
- Pydantic v2 (schemas/validation)
- JWT (django-ninja-jwt)
- Templates: HTMX (minimal hello page)
- DB: SQLite for dev; PostgreSQL recommended for prod

## App and Project Structure
The Django project config lives in `config/`, and the Django app is `src/user` (installed as `src.user`).
- Models: `src/user/models/` is a package (one model per file). Import via `from src.user.models import ...`.
- Schemas: `src/user/schemas/` contains Pydantic v2 schemas grouped by domain.
- Routers: `src/user/routers/` contains Django Ninja routers grouped by domain.
- API: `src/user/api.py` is the main NinjaAPI instance that registers all routers.
- Auth/JWT helpers: `src/user/auth.py` (Ninja auth classes), `src/user/backends.py`, `src/user/tokens.py` (custom token classes).
- Templates: `src/user/templates/`.

## Current Status
- Custom `User` model with email as username
- JWT Authentication: Uses `django-ninja-jwt` with custom token classes
  - `CustomAccessToken`: Includes global + per-service roles/permissions in claims
  - `CustomRefreshToken`: Supports token refresh functionality
- Django Ninja authentication:
  - `JWTAuth` class (Authorization: Bearer <token>) - wraps ninja-jwt with user status checks
  - `AdminAuth` class (extends JWTAuth, requires is_staff)
- Pydantic v2 schemas for all request/response validation
- Endpoints (admin-only unless noted):
  - POST `/api/auth/login` (open) — returns access + refresh JWT tokens for active users
  - POST `/api/auth/refresh` (open) — returns new access token using refresh token
  - Services: POST/GET `/api/services/`, GET/PATCH `/api/services/{id}`
  - Roles & Permissions per service:
    - POST/GET `/api/services/{service_id}/permissions`
    - POST/GET `/api/services/{service_id}/roles`
  - Users & assignments:
    - POST `/api/services/{service_id}/users`
    - GET/PATCH/DELETE `/api/users/{user_id}` (soft delete)
    - POST `/api/users/{user_id}/deactivate`, `/api/users/{user_id}/reactivate`
    - GET `/api/users/{user_id}/services`
    - PATCH/DELETE `/api/users/{user_id}/services/{service_id}`
- Minimal UI: `/` renders `hello.html`
- API Documentation: `/api/docs` (interactive Swagger UI)

## Configuration
Key settings live in `config/settings.py`:
- Custom user model: `src.user.models.user.User` (set via `AUTH_USER_MODEL`).
- Django Ninja: authentication handled per-endpoint via `auth=` parameter.
- JWT (django-ninja-jwt via `NINJA_JWT` settings):
  - `SIGNING_KEY`: From `JWT_SECRET` env var (set in prod)
  - `ALGORITHM`: Default HS256 (from `JWT_ALGORITHM` env var)
  - `ACCESS_TOKEN_LIFETIME`: Default 14 days (from `JWT_EXP_DELTA_SECONDS` env var)
  - `REFRESH_TOKEN_LIFETIME`: Default 30 days
  - `AUTH_TOKEN_CLASSES`: Uses custom `CustomAccessToken` class
- Legacy env vars retained for backward compatibility:
  - `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXP_DELTA_SECONDS`
- Email-based auth backend: `src.user.backends.EmailBackend`.

## How to Run (dev)
1. Create venv and install deps: `pip install -r admin/requirements/requirements.txt`
2. Migrate: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser --email admin@example.com`
4. Run: `python manage.py runserver`
5. Visit API docs: `http://127.0.0.1:8000/api/docs`

## Recent Changes
- Migrated from custom PyJWT implementation to django-ninja-jwt
- Added refresh token support for access token renewal
- Custom token classes preserve all existing claims (global/service permissions & roles)
- Updated authentication classes to wrap ninja-jwt with custom validation
- All tests updated to work with new token implementation

## Next Steps
1. Add permission checks and audit logging for admin endpoints
2. Add pagination/filters for list endpoints
3. Consider adding token blacklisting for logout functionality
4. Support key rotation and multiple JWT signing keys (kid)
5. Optional: Admin UI via HTMX

## Coding Guidelines
- PEP8 with 100-char line limit
- Strings are single quotes; docstrings use triple double quotes
- Python 3.12+ typing style (e.g., `str | None`)

## Documentation
- Keep root `README.md` up to date
- Additional docs live in `docs/` (lowercase filenames)
