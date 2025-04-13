"""
URL configuration for bloodbank project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('donations/', include('donations.urls')),
    path('inventory/', include('inventory.urls')),
    path('requests/', include('requests.urls')),
    path('dashboard/', include('dashboard.urls')),
]
