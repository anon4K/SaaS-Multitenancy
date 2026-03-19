from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_tenant, name='test_tenant'),
]
