from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):

    def process_request(self, request):
        hostname = request.get_host().split(':')[0]

        parts = hostname.split('.')
        if len(parts) > 1 and parts[0] != 'www':
            subdomain = parts[0]

            try:
                tenant = Tenant.objects.get(slug=subdomain, is_active=True)

                request.tenant = tenant

            except Tenant.DoesNotExist:
                request.tenant = None

        else:
            request.tenant = None

        return None