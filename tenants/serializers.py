from rest_framework import serializers
from .models import Tenant, User, Project
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

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
    

class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    tenant_slug = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'tenant_slug']
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def validate_tenant_slug(self, value):
        try:
            Tenant.objects.get(slug=value, is_active=True)
        except Tenant.DoesNotExist:
            raise serializers.ValidationError("Invalid tenant")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password2')
        tenant_slug = validated_data.pop('tenant_slug')
        
        tenant = Tenant.objects.get(slug=tenant_slug)
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            tenant=tenant,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled")
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include email and password")


class TenantRegistrationSerializer(serializers.ModelSerializer):
    
    admin_email = serializers.EmailField(write_only=True)
    admin_password = serializers.CharField(write_only=True, min_length=8)
    admin_first_name = serializers.CharField(write_only=True, required=False)
    admin_last_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Tenant
        fields = ['name', 'slug', 'admin_email', 'admin_password', 'admin_first_name', 'admin_last_name']
    
    def validate_slug(self, value):
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError("This company name is already taken")
        
        if not value.replace('-', '').isalnum() or value != value.lower():
            raise serializers.ValidationError("Slug must be lowercase alphanumeric with hyphens only")
        
        return value
    
    def create(self, validated_data):
        admin_email = validated_data.pop('admin_email')
        admin_password = validated_data.pop('admin_password')
        admin_first_name = validated_data.pop('admin_first_name', '')
        admin_last_name = validated_data.pop('admin_last_name', '')
        
        tenant = Tenant.objects.create(**validated_data)
        
        admin_user = User.objects.create_user(
            email=admin_email,
            password=admin_password,
            tenant=tenant,
            first_name=admin_first_name,
            last_name=admin_last_name,
            is_staff=True  
        )
        
        return tenant