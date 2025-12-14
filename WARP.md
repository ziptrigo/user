# Login Service Project

## Project Overview
Centralized Single Sign-On (SSO) service for ZipTrigo applications. Provides JWT-based user authentication, service (machine-to-machine) authentication via client_id/client_secret, centralized users/roles/permissions, and a minimal HTMX landing page.

## Goals
- Single source of truth for identity, roles and permissions
- Issue JWTs that client apps can validate
- Provide a clean REST API under `/api`
- Manage service-level credentials for first-party apps

## Tech Stack
- Python 3.13
- Django 6.0 + Django REST Framework (DRF)
- JWT (PyJWT)
- Templates: HTMX (minimal hello page)
- DB: SQLite for dev; PostgreSQL recommended for prod

## App and Project Structure
The Django project is named `login` and code lives under `src/`.

- Project config: `config/` (settings, urls, wsgi/asgi)
- Apps:
  - `src/accounts`: models, serializers, API views, app urls
  - `src/core`: authentication backends and JWT helpers
- Templates: `src/login/templates`

## Current Status
- Custom `User` model with email as username
- JWT utilities: `core/jwt.py` builds tokens including global + per-service roles/permissions
- DRF authentication:
  - `JWTUserAuthentication` (Authorization: Bearer <token>)
  - `ServiceAuthentication` (X-Client-Id / X-Client-Secret)
- Endpoints (admin-only unless noted):
  - POST `/api/auth/login` (open) — returns JWT for active users
  - Services: POST/GET `/api/services`, GET/PATCH `/api/services/{id}`
  - Roles & Permissions per service:
    - POST/GET `/api/services/{service_id}/permissions`
    - POST/GET `/api/services/{service_id}/roles`
  - Users & assignments:
    - POST `/api/services/{service_id}/users`
    - GET/PATCH/DELETE `/api/users/{user_id}` (soft delete)
    - POST `/api/users/{user_id}/deactivate`, `/reactivate`
    - GET `/api/users/{user_id}/services`
    - PATCH/DELETE `/api/users/{user_id}/services/{service_id}`
- Minimal UI: `/` renders `hello.html`

## Configuration
Key settings in `config/settings.py`:
- `AUTH_USER_MODEL = 'accounts.User'`
- DRF defaults to `IsAuthenticated`; admin endpoints add `IsAdminUser`
- JWT:
  - `JWT_SECRET` (set via env in prod)
  - `JWT_ALGORITHM = 'HS256'`
  - `JWT_EXP_DELTA_SECONDS = 14 * 24 * 3600`
- Email-based auth backend: `core.backends.EmailBackend`

## How to Run (dev)
1. Create venv and install deps: `pip install -r requirements.txt`
2. Migrate: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser --email admin@example.com`
4. Run: `python manage.py runserver`

## Next Steps
1. Add permission checks and audit logging for admin endpoints
2. Add pagination/filters for list endpoints
3. Add tests (unit + API) and CI pipeline
4. Support key rotation and multiple JWT signing keys (kid)
5. Optional: Admin UI via HTMX

## Coding Guidelines
- PEP8 with 100-char line limit
- Strings are single quotes; docstrings use triple double quotes
- Python 3.12+ typing style (e.g., `str | None`)

## Documentation
- Keep root `README.md` up to date
- Additional docs live in `docs/` (lowercase filenames)
