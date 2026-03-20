from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Tenant, User, Project
from .serializers import TenantSerializer, UserSerializer, ProjectSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    TenantSerializer, UserSerializer, ProjectSerializer, UserRegistrationSerializer,
    UserLoginSerializer, TenantRegistrationSerializer
)


def test_tenant(request):
    
    if hasattr(request, 'tenant') and request.tenant:
        return JsonResponse({
            'success': True,
            'tenant_name': request.tenant.name,
            'tenant_slug': request.tenant.slug,
            'message': f'You are accessing {request.tenant.name}!'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'No tenant detected (accessing from main domain)'
        })


def list_projects(request):
    
    projects = Project.objects.all()
    
    project_list = [
        {
            'id': p.pk,
            'name': p.name,
            'tenant': p.tenant.name,
            'created_at': p.created_at.isoformat()
        }
        for p in projects
    ]
    
    return JsonResponse({
        'tenant': request.tenant.name if request.tenant else 'No tenant',
        'project_count': len(project_list),
        'projects': project_list
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'tenant': user.tenant.name
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'tenant': user.tenant.name,
                'tenant_slug': user.tenant.slug
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    return Response({
        'message': 'Logout successful. Token will expire naturally.'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register_tenant(request):
    serializer = TenantRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        tenant = serializer.save()
        
        admin_user = User.objects.get(tenant=tenant, is_staff=True)
        
        refresh = RefreshToken.for_user(admin_user)
        
        return Response({
            'message': 'Tenant registered successfully',
            'tenant': {
                'name': tenant.name,
                'slug': tenant.slug,
            },
            'admin': {
                'email': admin_user.email,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'subdomain': f'{tenant.slug}.yourapp.com'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    
    return Response({
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'tenant': user.tenant.name,
        'tenant_slug': user.tenant.slug,
        'is_staff': user.is_staff
    })
class ProjectViewSet(viewsets.ModelViewSet):
    
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated] 
    
    def get_queryset(self):
        return Project.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        if 'tenant' in serializer.validated_data:
            serializer.validated_data.pop('tenant')
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        project = self.get_object()
        project.is_active = not project.is_active
        project.save()
        
        serializer = self.get_serializer(project)
        return Response(serializer.data)

class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Tenant.objects.filter(id=self.request.tenant.id)
        return Tenant.objects.none()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return User.objects.filter(tenant=self.request.tenant)
        return User.objects.none()