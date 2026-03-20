from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Tenant, User, Project
from .serializers import TenantSerializer, UserSerializer, ProjectSerializer


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

class ProjectViewSet(viewsets.ModelViewSet):
    
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]  
    
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