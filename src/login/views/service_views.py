import secrets

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from src.login.models import Service
from src.login.serializers import ServiceSerializer


class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # Generate client_id and client_secret
        client_id = secrets.token_urlsafe(32)
        client_secret = secrets.token_urlsafe(64)
        serializer.save(client_id=client_id, client_secret=client_secret)


class ServiceDetailView(generics.RetrieveUpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'service_id'
