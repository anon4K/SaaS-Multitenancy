from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, tenant,password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not tenant:
            raise ValueError('Tenant is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, tenant=tenant, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        system_tenant, _ = Tenant.objects.get_or_create(
            slug = 'system',
            defaults={'name': 'System Tenant'}
        )       

        return self.create_user(email, system_tenant, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='users'
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='tenant_users',
        related_query_name='tenant_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='tenant_users',
        related_query_name='tenant_user',
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        ordering = ['email']
    
    def __str__(self):
        return f"{self.email} ({self.tenant.name})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email   

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects_created'
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"
    
