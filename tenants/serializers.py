from rest_framework import serializers
from .models import Tenant, User, Project

from rest_framework import serializers
from .models import Tenant, User, Project


class TenantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'tenant', 'tenant_name', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'tenant': {'write_only': True}  
        }


class ProjectSerializer(serializers.ModelSerializer):
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 
            'tenant', 'tenant_name',
            'created_by', 'created_by_email',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        
        if hasattr(request, 'tenant') and request.tenant:
            validated_data['tenant'] = request.tenant
        else:
            raise serializers.ValidationError("No tenant context available")
        
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)