from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('create/', views.create_request, name='create_request'),
    path('<int:request_id>/', views.request_detail, name='request_detail'),
    path('<int:request_id>/cancel/', views.cancel_request, name='cancel_request'),
    path('<int:request_id>/respond/', views.respond_to_request, name='respond_to_request'),
    path('export/', views.export_requests, name='export_requests'),
]
