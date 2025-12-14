from django.urls import path

from accounts.views import role_permission_views, service_views, user_views
from accounts.views.auth_views import LoginView

urlpatterns = [
    # Auth (Login)
    path('auth/login', LoginView.as_view(), name='api-login'),
    # Services
    path('services', service_views.ServiceListCreateView.as_view(), name='service-list-create'),
    path(
        'services/<uuid:service_id>',
        service_views.ServiceDetailView.as_view(),
        name='service-detail',
    ),
    # Service permissions & roles
    path(
        'services/<uuid:service_id>/permissions',
        role_permission_views.ServicePermissionListCreateView.as_view(),
        name='service-permissions',
    ),
    path(
        'services/<uuid:service_id>/roles',
        role_permission_views.ServiceRoleListCreateView.as_view(),
        name='service-roles',
    ),
    # Users
    path(
        'services/<uuid:service_id>/users',
        user_views.ServiceUserCreateView.as_view(),
        name='service-user-create',
    ),
    path(
        'users/<uuid:user_id>', user_views.UserDetailUpdateDeleteView.as_view(), name='user-detail'
    ),
    path(
        'users/<uuid:user_id>/deactivate',
        user_views.UserDeactivateView.as_view(),
        name='user-deactivate',
    ),
    path(
        'users/<uuid:user_id>/reactivate',
        user_views.UserReactivateView.as_view(),
        name='user-reactivate',
    ),
    path(
        'users/<uuid:user_id>/services',
        user_views.UserServicesListView.as_view(),
        name='user-services',
    ),
    path(
        'users/<uuid:user_id>/services/<uuid:service_id>',
        user_views.UserServiceAssignmentView.as_view(),
        name='user-service-assignment',
    ),
]
