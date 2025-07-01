from django.contrib import admin
from .models import InventoryItem
from .models import InventoryRequest
from .models import UserGroup


admin.site.register(InventoryRequest)
admin.site.register(UserGroup)

#This tells us i want the Inventory Item model to show up in the admin panel so I can CRUD in the UI

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ('name', 'quantity', 'location')

    # Add a search box to allow searching by item name or location
    search_fields = ('name', 'location')

    # Add filters for the 'name' and 'location' fields in the sidebar
    list_filter = ('name', 'location')

    # Enable inline editing for quantity and location
    list_editable = ('quantity', 'location')

    # Show 20 items per page
    list_per_page = 20