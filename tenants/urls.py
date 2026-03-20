from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'tenants', views.TenantViewSet, basename='tenant')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('test/', views.test_tenant, name='test_tenant'),
    path('projects-simple/', views.list_projects, name='list_projects'),
    
    path('api/auth/register/', views.register_user, name='register_user'),
    path('api/auth/login/', views.login_user, name='login_user'),
    path('api/auth/logout/', views.logout_user, name='logout_user'),
    path('api/auth/me/', views.current_user, name='current_user'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/register-tenant/', views.register_tenant, name='register_tenant'),
    
    path('api/', include(router.urls)),
]