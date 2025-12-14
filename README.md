# Login Service

Centralized Single Sign-On (SSO) authentication and authorization service for ZipTrigo web applications.

## Overview

The Login service provides:
- **Single Sign-On (SSO)** across multiple first-party web apps
- **Centralized identity, roles, and permissions** management
- **JWT-based authentication** for users
- **Client ID/Secret authentication** for services
- **RESTful API** under `/api`

## Tech Stack

- Backend: Django 6.0, Python 3.13, Django REST Framework
- Frontend: HTMX (minimal landing page)
- Database: SQLite (development) / PostgreSQL (production)

## Installation

1. Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser --email admin@example.com
```

5. Start development server:
```bash
python manage.py runserver
```

## API Endpoints

### API Documentation
- `/api/schema/` - OpenAPI schema (append `?format=json` or `?format=yaml`)
- `/api/docs/` - Interactive Swagger UI documentation (supports Authorize with Bearer tokens)
- `/api/redoc/` - ReDoc documentation

### Authentication

- Auth method: JWT via `Authorization: Bearer <token>`.
- Service-to-service auth: `X-Client-Id` and `X-Client-Secret` headers (for endpoints that use `ServiceAuthentication`).

**Login (open endpoint)**
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response 200:
{
  "access_token": "eyJ...",
  "expires_in": 1209600,
  "token_type": "Bearer"
}
```

### Services (Admin only)

Create a service to obtain `client_id` and `client_secret` the first time.

- `POST /api/services` - Create a new service
- `GET /api/services` - List all services
- `GET /api/services/{id}` - Get service details
- `PATCH /api/services/{id}` - Update service

### Permissions & Roles (Admin only)

- `POST /api/services/{service_id}/permissions` - Create permission for service
- `GET /api/services/{service_id}/permissions` - List service permissions
- `POST /api/services/{service_id}/roles` - Create role for service
- `GET /api/services/{service_id}/roles` - List service roles

### User Management (Admin only)

- `POST /api/services/{service_id}/users` - Create/assign user to service
- `GET /api/users/{user_id}` - Get user details
- `PATCH /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Soft delete user
- `POST /api/users/{user_id}/deactivate` - Deactivate user
- `POST /api/users/{user_id}/reactivate` - Reactivate user
- `GET /api/users/{user_id}/services` - List user's service assignments
- `PATCH /api/users/{user_id}/services/{service_id}` - Update user roles/permissions
- `DELETE /api/users/{user_id}/services/{service_id}` - Remove service assignment

## Authentication Methods

### User Authentication (JWT)

Include JWT token in Authorization header:
```
Authorization: Bearer <token>
```

### Service Authentication

Include client credentials in headers:
```
X-Client-Id: <client_id>
X-Client-Secret: <client_secret>
```

## JWT Payload Structure

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234567890,
  "global_permissions": ["admin", "manage_users"],
  "global_roles": ["super_admin"],
  "services": {
    "service-uuid": {
      "permissions": ["read", "write"],
      "roles": ["editor"]
    }
  }
}
```

## Configuration

Key settings in `config/settings.py`:

- `AUTH_USER_MODEL = 'accounts.User'`
- DRF defaults: `IsAuthenticated`; admin endpoints layer `IsAdminUser`
- `JWT_SECRET` - Secret key for JWT signing (set via environment in production)
- `JWT_ALGORITHM` - Algorithm for JWT (default: HS256)
- `JWT_EXP_DELTA_SECONDS` - Token expiration time (default: 2 weeks)

## Testing

Default superuser credentials for local testing (if you created as shown above):
- Email: `admin@example.com`
- Password: `admin123`

Quick manual test sequence:
1) Create a service (admin-only): `POST /api/services` — returns generated `client_id` and `client_secret`.
2) Create or assign a user to that service: `POST /api/services/{service_id}/users`.
3) Login as that user: `POST /api/auth/login` — receive JWT.
4) Call protected endpoints with `Authorization: Bearer <token>`.

Django admin: http://127.0.0.1:8000/admin/

## Project Structure

```
manage.py           # Django management script
requirements.txt    # Python dependencies
docs/               # Documentation
src/                # Source code
  login/            # App namespace (templates, etc.)
    templates/      # HTML templates
config/             # Django project configuration
  settings.py       # Settings
  urls.py           # Main URL routing
  wsgi.py           # WSGI application
  asgi.py           # ASGI application
  core/             # Core functionality
    jwt.py          # JWT utilities
    authentication.py  # DRF authentication classes
    backends.py     # Django authentication backend
  accounts/         # Main app
    models.py       # Data models
    serializers.py  # DRF serializers
    views/          # API views
      auth_views.py
      service_views.py
      role_permission_views.py
      user_views.py
    urls.py         # App URL routing
    admin.py        # Admin configuration
  templates/        # HTML templates
    base.html
    hello.html
```

## License

See LICENSE file for details.
