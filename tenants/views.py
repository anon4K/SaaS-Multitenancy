from django.http import JsonResponse
from .models import Project


def test_tenant(request):
    """Test view to see which tenant is detected"""
    
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
        }
        for p in projects
    ]

    return JsonResponse({
        'tenant': request.tenant.name if request.tenant else 'No tenant',
        'project_count': len(project_list),
        'projects': project_list
    })
