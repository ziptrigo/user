import jwt
import time
from django.conf import settings
from accounts.models import (
    UserServiceAssignment,
    UserServiceRole,
    UserServicePermission,
    UserGlobalRole,
    UserGlobalPermission,
    RolePermission,
)


def build_jwt_for_user(user) -> tuple[str, int]:
    """
    Build JWT token for a user with all permissions and roles.

    Returns:
        tuple: (token_string, expires_in_seconds)
    """
    now = int(time.time())
    exp = now + settings.JWT_EXP_DELTA_SECONDS

    # Collect global permissions
    global_perms = set()
    direct_global_perms = UserGlobalPermission.objects.filter(
        user=user
    ).select_related('permission')
    for ugp in direct_global_perms:
        global_perms.add(ugp.permission.code)

    # Collect global roles and their permissions
    global_roles = []
    user_global_roles = UserGlobalRole.objects.filter(
        user=user
    ).select_related('role')
    for ugr in user_global_roles:
        global_roles.append(ugr.role.name)
        role_perms = RolePermission.objects.filter(
            role=ugr.role
        ).select_related('permission')
        for rp in role_perms:
            global_perms.add(rp.permission.code)

    # Collect service-specific data
    services_data = {}
    assignments = UserServiceAssignment.objects.filter(
        user=user
    ).select_related('service')

    for assignment in assignments:
        service_id = str(assignment.service.id)
        service_perms = set()
        service_roles = []

        # Direct service permissions
        direct_perms = UserServicePermission.objects.filter(
            user=user, service=assignment.service
        ).select_related('permission')
        for usp in direct_perms:
            service_perms.add(usp.permission.code)

        # Service roles and their permissions
        user_roles = UserServiceRole.objects.filter(
            user=user, service=assignment.service
        ).select_related('role')
        for usr in user_roles:
            service_roles.append(usr.role.name)
            role_perms = RolePermission.objects.filter(
                role=usr.role
            ).select_related('permission')
            for rp in role_perms:
                service_perms.add(rp.permission.code)

        services_data[service_id] = {
            'permissions': sorted(list(service_perms)),
            'roles': service_roles,
        }

    payload = {
        'sub': str(user.id),
        'email': user.email,
        'iat': now,
        'exp': exp,
        'global_permissions': sorted(list(global_perms)),
        'global_roles': global_roles,
        'services': services_data,
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token, settings.JWT_EXP_DELTA_SECONDS


def decode_jwt(token: str) -> dict:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded payload

    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )