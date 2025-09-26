from django.contrib import admin
from .models import MenuItem, Order, OrderItem, RestaurantProfile

@admin.register(RestaurantProfile)
class RestaurantProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_tables', 'currently_occupied_tables', 'avg_dine_in_duration_minutes')
    fields = ('name', 'total_tables', 'currently_occupied_tables', 'avg_dine_in_duration_minutes')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'estimated_prep_time_minutes')
    list_filter = ('estimated_prep_time_minutes',)
    search_fields = ('name', 'description')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'customer_name', 'status', 'queue_position', 'target_arrival_time', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_code', 'customer_name')
    readonly_fields = ('order_code', 'created_at', 'queue_position')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_code', 'customer_name', 'status', 'created_at')
        }),
        ('Queue Management', {
            'fields': ('queue_position', 'target_arrival_time')
        }),
        ('Timing Analytics', {
            'fields': ('seated_at_time', 'completed_at_time')
        }),
    )
