from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('update/', views.update_inventory, name='update_inventory'),
    path('export/', views.export_inventory, name='export_inventory'),
    path('logs/', views.inventory_logs, name='inventory_logs'),
]
