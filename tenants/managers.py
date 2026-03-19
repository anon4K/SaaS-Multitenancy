from django.db import models


class TenantManager(models.Manager):
    
    def __init__(self, *args, **kwargs):
        self.tenant = None
        super().__init__(*args, **kwargs)
    
    def set_tenant(self, tenant):
        self.tenant = tenant
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.tenant is not None:
            return queryset.filter(tenant=self.tenant)
        
        return queryset
