from django.urls import path
from . import views  # Import views from the current app
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home & Success
    path('', views.home, name='home'),
    path('success/', views.success_view, name='success'),

    # Leads
    path('leads/', views.leads_view, name='leads_view'),
    path('leads/create/', views.create_lead_view, name='create_lead'),
    path('leads/edit/<uuid:lead_id>/', views.edit_lead_view, name='edit_lead'),
    path('leads/delete/<uuid:lead_id>/', views.delete_lead_view, name='delete_lead'),

    # Vendors
    path('vendors/', views.vendors_view, name='vendors_view'),
    path('vendors/create/', views.create_vendor_view, name='create_vendor'),
    path('vendors/edit/<uuid:vendor_id>/', views.edit_vendor_view, name='edit_vendor'),
    path('vendors/delete/<uuid:vendor_id>/', views.delete_vendor_view, name='delete_vendor'),

    # Locations
    path('locations/', views.locations_view, name='locations_view'),
    path('locations/create/', views.create_location_view, name='create_location'),
    path('locations/edit/<uuid:location_id>/', views.edit_location_view, name='edit_location'),
    path('locations/delete/<uuid:location_id>/', views.delete_location_view, name='delete_location'),

    # Districts
    path('districts/', views.districts_view, name='districts_view'),
    path('districts/create/', views.create_district_view, name='create_district'),
    path('districts/edit/<uuid:district_id>/', views.edit_district_view, name='edit_district'),
    path('districts/delete/<uuid:district_id>/', views.delete_district_view, name='delete_district'),

    # Services
    path('services/', views.services_view, name='services_view'),
    path('services/create/', views.create_service_view, name='create_service'),
    path('services/edit/<uuid:service_id>/', views.edit_service_view, name='edit_service'),
    path('services/delete/<uuid:service_id>/', views.delete_service_view, name='delete_service'),

    # User Registration & Authentication
    path('register/', views.register_view, name='register'),
    path('registration-feedback/', views.registration_feedback_view, name='registration_feedback'),
    path('pending-users/', views.pending_users_view, name='pending_users'),
    path('approve-user/<int:user_id>/', views.approve_user_view, name='approve_user'),
    path('assign-group/<int:user_id>/', views.assign_group_view, name='assign_group'),

    # Auth (Login/Logout/Dashboard Redirect)
    path('login/', auth_views.LoginView.as_view(template_name='services/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='services/login.html')),  # For @login_required redirects
    path('dashboard/', views.redirect_dashboard_view, name='redirect_dashboard'),
    path('dashboard/it/', views.it_dashboard_view, name='it_dashboard'),
    path('dashboard/director/', views.director_dashboard_view, name='director_dashboard'),
    path('dashboard/rm/', views.rm_dashboard_view, name='rm_dashboard'),

    # AJAX Dependent Dropdown
    path('ajax/load-locations/', views.load_locations, name='ajax_load_locations'),
]

# Serve static files in local production mode
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
