from django.http import JsonResponse


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