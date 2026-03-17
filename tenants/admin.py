from django.contrib import admin
from .models import Tenant, User, Project


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'tenant', 'first_name', 'last_name', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    list_filter = ['tenant', 'is_active', 'is_staff', 'date_joined']
    readonly_fields = ['date_joined']
    
    fieldsets = (
        ('User Info', {
            'fields': ('email', 'first_name', 'last_name', 'password')
        }),
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('date_joined',)
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'created_by', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['tenant', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']