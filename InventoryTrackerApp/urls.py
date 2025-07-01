from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin portal
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Login
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard
    path('logout/', views.logout_view, name='logout'),  # Logout
    path('available-inventory/', views.available_inventory, name='available_inventory'),  # View inventory
    path('create-request/', views.create_request, name='create_request'),  # Create request
    path('delete-request/<int:request_id>/', views.delete_request, name='delete_request'),
    path('edit-request/<int:request_id>/', views.edit_request, name='edit_request')
]
