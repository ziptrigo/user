from rest_framework import serializers

from src.login.models import Permission, Role, RolePermission, Service, User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    expires_in = serializers.IntegerField()
    token_type = serializers.CharField(default='Bearer')


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'description',
            'client_id',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'client_id', 'created_at', 'updated_at']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            'id',
            'type',
            'service',
            'code',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Role
        fields = [
            'id',
            'service',
            'name',
            'description',
            'permissions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        permission_codes = validated_data.pop('permissions', [])
        role = Role.objects.create(**validated_data)

        # Map permission codes to Permission objects
        if permission_codes:
            service = validated_data.get('service')
            if service:
                permissions = Permission.objects.filter(service=service, code__in=permission_codes)
            else:
                permissions = Permission.objects.filter(
                    type=Permission.TYPE_GLOBAL, code__in=permission_codes
                )

            for permission in permissions:
                RolePermission.objects.create(role=role, permission=permission)

        return role

    def update(self, instance, validated_data):
        permission_codes = validated_data.pop('permissions', None)

        # Update basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Update permissions if provided
        if permission_codes is not None:
            # Remove existing permissions
            RolePermission.objects.filter(role=instance).delete()

            # Add new permissions
            service = instance.service
            if service:
                permissions = Permission.objects.filter(service=service, code__in=permission_codes)
            else:
                permissions = Permission.objects.filter(
                    type=Permission.TYPE_GLOBAL, code__in=permission_codes
                )

            for permission in permissions:
                RolePermission.objects.create(role=instance, permission=permission)

        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'status',
            'inactive_at',
            'inactive_reason',
            'deleted_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'inactive_at',
            'inactive_reason',
            'deleted_at',
            'created_at',
            'updated_at',
        ]


class CreateServiceUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    roles = serializers.ListField(child=serializers.CharField(), required=False)
    permissions = serializers.ListField(child=serializers.CharField(), required=False)
