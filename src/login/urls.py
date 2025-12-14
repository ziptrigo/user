from django.urls import path

from .api import roles_permissions, services, users
from .api.auth import LoginView

urlpatterns = [
    # Auth (Login)
    path('auth/login', LoginView.as_view(), name='api-login'),
    # Services
    path('services', services.ServiceListCreateView.as_view(), name='service-list-create'),
    path(
        'services/<uuid:service_id>',
        services.ServiceDetailView.as_view(),
        name='service-detail',
    ),
    # Service permissions & roles
    path(
        'services/<uuid:service_id>/permissions',
        roles_permissions.ServicePermissionListCreateView.as_view(),
        name='service-permissions',
    ),
    path(
        'services/<uuid:service_id>/roles',
        roles_permissions.ServiceRoleListCreateView.as_view(),
        name='service-roles',
    ),
    # Users
    path(
        'services/<uuid:service_id>/users',
        users.ServiceUserCreateView.as_view(),
        name='service-user-create',
    ),
    path('users/<uuid:user_id>', users.UserDetailUpdateDeleteView.as_view(), name='user-detail'),
    path(
        'users/<uuid:user_id>/deactivate',
        users.UserDeactivateView.as_view(),
        name='user-deactivate',
    ),
    path(
        'users/<uuid:user_id>/reactivate',
        users.UserReactivateView.as_view(),
        name='user-reactivate',
    ),
    path(
        'users/<uuid:user_id>/services',
        users.UserServicesListView.as_view(),
        name='user-services',
    ),
    path(
        'users/<uuid:user_id>/services/<uuid:service_id>',
        users.UserServiceAssignmentView.as_view(),
        name='user-service-assignment',
    ),
]
