from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin portal
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Login
    path('dashboard/', views.dashboard, name='dashboard'),  # Unified dashboard
    path('logout/', views.logout_view, name='logout'),  # Logout
    path('available-inventory/', views.available_inventory, name='available_inventory'),  # View inventory
    path('create-request/', views.create_request, name='create_request'),  # Create request
    path('requests/edit/<int:request_id>/', views.edit_request, name='edit_request'),  # Edit request (Admin only)
    path('requests/delete/<int:request_id>/', views.delete_request, name='delete_request'),
    # Delete request (Admin only)
]
