import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    client_id = models.CharField(max_length=64, unique=True)
    client_secret = models.CharField(max_length=128)
    status = models.CharField(
        max_length=32,
        choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')],
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Permission(models.Model):
    TYPE_GLOBAL = 'GLOBAL'
    TYPE_SERVICE = 'SERVICE'
    TYPE_CHOICES = [
        (TYPE_GLOBAL, 'Global'),
        (TYPE_SERVICE, 'Service'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    service = models.ForeignKey(
        'Service',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='permissions',
    )
    code = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'code'],
                condition=Q(type='GLOBAL'),
                name='unique_global_permission_code',
            ),
            models.UniqueConstraint(
                fields=['type', 'service', 'code'],
                condition=Q(type='SERVICE'),
                name='unique_service_permission_code',
            ),
        ]

    def __str__(self):
        return f'{self.type}:{self.code}'


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        'Service',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='roles',
    )
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'name'],
                name='unique_role_name_per_service',
            )
        ]

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey('Permission', on_delete=models.CASCADE, related_name='permission_roles')

    class Meta:
        unique_together = ('role', 'permission')


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_DELETED = 'DELETED'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_DELETED, 'Deleted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    inactive_at = models.DateTimeField(null=True, blank=True)
    inactive_reason = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def mark_deleted(self):
        self.status = self.STATUS_DELETED
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def deactivate(self, reason=''):
        self.status = self.STATUS_INACTIVE
        self.inactive_at = timezone.now()
        self.inactive_reason = reason
        self.save(update_fields=['status', 'inactive_at', 'inactive_reason'])

    def reactivate(self):
        self.status = self.STATUS_ACTIVE
        self.inactive_at = None
        self.inactive_reason = ''
        self.save(update_fields=['status', 'inactive_at', 'inactive_reason'])

    def __str__(self):
        return self.email


class UserServiceAssignment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='service_assignments')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='user_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_assignments',
    )

    class Meta:
        unique_together = ('user', 'service')


class UserServiceRole(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='service_roles')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey('Role', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'service', 'role')


class UserServicePermission(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='service_permissions')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='user_permissions')
    permission = models.ForeignKey('Permission', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'service', 'permission')


class UserGlobalRole(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='global_roles')
    role = models.ForeignKey('Role', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')


class UserGlobalPermission(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='global_permissions')
    permission = models.ForeignKey('Permission', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'permission')
