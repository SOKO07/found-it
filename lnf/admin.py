from django.contrib import admin
from .models import Category, Item, PendingCategory

@admin.action(description='Approve selected pending categories')
def approve_categories(modeladmin, request, queryset):
    for pending_category in queryset:
        # Create a new Category
        category, created = Category.objects.get_or_create(name=pending_category.name)
        
        # Find and update items with the pending category name
        items_to_update = Item.objects.filter(pending_category_name__iexact=pending_category.name)
        for item in items_to_update:
            item.category = category
            item.pending_category_name = None # Clear the pending name
            item.save()
            
        # Delete the pending category
        pending_category.delete()

class PendingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    actions = [approve_categories]

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'get_holding_users', 'found_date', 'pub_date', 'uploaded_by')
    list_filter = ('status', 'found_date', 'pub_date', 'uploaded_by')
    list_editable = ('status',)
    search_fields = ('name', 'description')
    readonly_fields = ('get_holding_users',)
    autocomplete_fields = ('retrieved_by',)

    def get_holding_users(self, obj):
        return ", ".join([user.username for user in obj.held_by.all()])
    get_holding_users.short_description = 'Holding Users'

admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(PendingCategory, PendingCategoryAdmin)