from django.urls import path
from django.shortcuts import redirect
from . import views
from django.conf.urls import handler404
from .views import custom_404_view

handler404 = custom_404_view

urlpatterns = [
    path('', lambda request: redirect('login', permanent=True)),
    
    # Logout and login
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Pools
    path('pools/', views.pool_list, name='pool_list'),
    path('pools/add/', views.pool_create, name='pool_create'),
    path('pools/edit/<int:pk>/', views.pool_update, name='pool_update'),
    path('pools/delete/<int:pk>/', views.pool_delete, name='pool_delete'),

    # Lifeguards
    path('lifeguards/', views.lifeguard_list, name='lifeguard_list'),
    path('lifeguards/add/', views.lifeguard_create, name='lifeguard_create'),
    path('lifeguards/edit/<int:pk>/', views.lifeguard_update, name='lifeguard_update'),
    path('lifeguards/delete/<int:pk>/', views.lifeguard_delete, name='lifeguard_delete'),

    # Shifts
    path('shifts/', views.shift_list, name='shift_list'),
    path('shifts/add/', views.shift_create, name='shift_create'),
    path('shifts/edit/<int:pk>/', views.shift_update, name='shift_update'),
    path('shifts/delete/<int:pk>/', views.shift_delete, name='shift_delete'),
    path('shifts/lifeguard/', views.shift_list_lifeguard, name='shift_list_lifeguard'),

    # Applications
    path('applications/', views.application_list, name='application_list'),
    path('applications/add/<int:shift_id>/', views.application_create, name='application_create'),
    path('applications/delete/<int:pk>/', views.application_delete, name='application_delete'),
    path('applications/lifeguard/', views.application_list_lifeguard, name='application_list_lifeguard'),
    path('applications/update-status/<int:pk>/', views.application_status_update, name='application_status_update'),

    # Incidents
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/lifeguard/', views.incident_list_lifeguard, name='incident_list_lifeguard'),
    path('incidents/add/', views.incident_create, name='incident_create'),
    path('incidents/edit/<int:incident_id>/', views.incident_update, name='incident_update'),
    path('incidents/delete/<int:incident_id>/', views.incident_delete, name='incident_delete'),
]
