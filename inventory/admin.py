from django.contrib import admin
from .models import InventoryItem
from .models import InventoryRequest
from .models import UserGroup


admin.site.register(InventoryRequest)
admin.site.register(UserGroup)


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'location')

    search_fields = ('name', 'location')

    list_filter = ('name', 'location')

    list_editable = ('quantity', 'location')

    # Show 20 items per page
    list_per_page = 20