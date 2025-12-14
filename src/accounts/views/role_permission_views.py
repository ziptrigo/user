from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from accounts.models import Permission, Role, Service
from accounts.serializers import PermissionSerializer, RoleSerializer


class ServicePermissionListCreateView(generics.ListCreateAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        service_id = self.kwargs['service_id']
        return Permission.objects.filter(service_id=service_id)

    def perform_create(self, serializer):
        service_id = self.kwargs['service_id']
        service = Service.objects.get(id=service_id)
        serializer.save(service=service, type=Permission.TYPE_SERVICE)


class ServiceRoleListCreateView(generics.ListCreateAPIView):
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        service_id = self.kwargs['service_id']
        return Role.objects.filter(service_id=service_id)

    def perform_create(self, serializer):
        service_id = self.kwargs['service_id']
        service = Service.objects.get(id=service_id)
        serializer.save(service=service)
