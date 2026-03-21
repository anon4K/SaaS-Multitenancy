from django.contrib.auth.backends import BaseBackend
from tenants.models import User


class EmailBackend(BaseBackend):
    
    def authenticate(self, request, username=None, password=None, **kwargs):        
        email = username
        
        if not email or not password:
            return None
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None