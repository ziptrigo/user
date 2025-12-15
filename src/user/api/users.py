from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import (
    Permission,
    Role,
    Service,
    User,
    UserServiceAssignment,
    UserServicePermission,
    UserServiceRole,
)
from ..serializers import CreateServiceUserSerializer, UserSerializer


class ServiceUserCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, service_id):
        serializer = CreateServiceUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        name = serializer.validated_data.get('name', '')
        password = serializer.validated_data.get('password')
        role_names = serializer.validated_data.get('roles', [])
        permission_codes = serializer.validated_data.get('permissions', [])

        # Get or create user
        user, created = User.objects.get_or_create(email=email, defaults={'name': name})

        if created and password:
            user.set_password(password)
            user.save()

        # Get service
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'detail': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create service assignment
        assignment, _ = UserServiceAssignment.objects.get_or_create(
            user=user, service=service, defaults={'created_by': request.user}
        )

        # Assign roles
        for role_name in role_names:
            try:
                role = Role.objects.get(service=service, name=role_name)
                UserServiceRole.objects.get_or_create(user=user, service=service, role=role)
            except Role.DoesNotExist:
                pass

        # Assign permissions
        for perm_code in permission_codes:
            try:
                permission = Permission.objects.get(service=service, code=perm_code)
                UserServicePermission.objects.get_or_create(
                    user=user, service=service, permission=permission
                )
            except Permission.DoesNotExist:
                pass

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class UserDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    def perform_destroy(self, instance):
        instance.mark_deleted()


class UserDeactivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', '')
        user.deactivate(reason)

        return Response(UserSerializer(user).data)


class UserReactivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.reactivate()

        return Response(UserSerializer(user).data)


class UserServicesListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        assignments = UserServiceAssignment.objects.filter(user=user).select_related('service')

        services_data = []
        for assignment in assignments:
            service = assignment.service

            # Get roles
            roles = UserServiceRole.objects.filter(user=user, service=service).select_related(
                'role'
            )
            role_names = [usr.role.name for usr in roles]

            # Get permissions
            perms = UserServicePermission.objects.filter(user=user, service=service).select_related(
                'permission'
            )
            perm_codes = [usp.permission.code for usp in perms]

            services_data.append(
                {
                    'service_id': str(service.id),
                    'service_name': service.name,
                    'roles': role_names,
                    'permissions': perm_codes,
                }
            )

        return Response(services_data)


class UserServiceAssignmentView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id, service_id):
        try:
            user = User.objects.get(id=user_id)
            service = Service.objects.get(id=service_id)
        except (User.DoesNotExist, Service.DoesNotExist):
            return Response(
                {'detail': 'User or service not found'}, status=status.HTTP_404_NOT_FOUND
            )

        role_names = request.data.get('roles', [])
        permission_codes = request.data.get('permissions', [])

        # Clear existing roles
        UserServiceRole.objects.filter(user=user, service=service).delete()

        # Assign new roles
        for role_name in role_names:
            try:
                role = Role.objects.get(service=service, name=role_name)
                UserServiceRole.objects.create(user=user, service=service, role=role)
            except Role.DoesNotExist:
                pass

        # Clear existing permissions
        UserServicePermission.objects.filter(user=user, service=service).delete()

        # Assign new permissions
        for perm_code in permission_codes:
            try:
                permission = Permission.objects.get(service=service, code=perm_code)
                UserServicePermission.objects.create(
                    user=user, service=service, permission=permission
                )
            except Permission.DoesNotExist:
                pass

        return Response({'detail': 'Updated successfully'})

    def delete(self, request, user_id, service_id):
        try:
            user = User.objects.get(id=user_id)
            service = Service.objects.get(id=service_id)
        except (User.DoesNotExist, Service.DoesNotExist):
            return Response(
                {'detail': 'User or service not found'}, status=status.HTTP_404_NOT_FOUND
            )

        # Delete all associations
        UserServiceAssignment.objects.filter(user=user, service=service).delete()
        UserServiceRole.objects.filter(user=user, service=service).delete()
        UserServicePermission.objects.filter(user=user, service=service).delete()

        return Response({'detail': 'Assignment removed'}, status=status.HTTP_204_NO_CONTENT)
