from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'tenants', views.TenantViewSet, basename='tenant')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('test/', views.test_tenant, name='test_tenant'),
    path('projects/', views.list_projects, name='list_projects'),

    path('api/', include(router.urls)),
]
