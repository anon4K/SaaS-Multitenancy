from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Tenant, Project
from .managers import TenantManager


class TenantMiddleware(MiddlewareMixin):

    def process_request(self, request):
        hostname = request.get_host().split(':')[0]

        parts = hostname.split('.')
        if len(parts) > 1 and parts[0] != 'www':
            subdomain = parts[0]

            try:
                tenant = Tenant.objects.get(slug=subdomain, is_active=True)

                request.tenant = tenant

                Project.objects.set_tenant(tenant) #type: ignore

            except Tenant.DoesNotExist:
                request.tenant = None
                Project.objects.set_tenant(None) #type: ignore

        else:
            request.tenant = None
            Project.objects.set_tenant(None)  #type: ignore

        return None