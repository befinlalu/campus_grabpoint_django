from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Category,Product,Order, OrderItem
 

class CustomUserAdmin(UserAdmin):
    # Specify the fields to be displayed in the user list
    list_display = ('username', 'email', 'full_name', 'phone_number', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'full_name', 'phone_number')  # Enable search by username, email, full name, and phone number
    ordering = ('username',)

    # Fields to be displayed when editing a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Fields to be displayed in the form to add/edit a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'full_name', 'phone_number', 'is_verified', 'is_active')
        }),
    )
    # Make sure to set this so the user model is editable through the admin interface
    filter_horizontal = ('groups', 'user_permissions',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Only display the name
    search_fields = ("name",)  # Allow searching by category name
    ordering = ("name",)  # Sort by name

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_description', 'price', 'available_quantity', 'sale_price', 'category')  # Customize displayed fields
    search_fields = ('name', 'category__name')  # Allow searching by product name and category name
    list_filter = ('category',)  # Filter products by category



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty forms to display by default

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['user__username', 'status', 'payment_status']
    inlines = [OrderItemInline]  # Include order items inline in the order view

    # Optional: Add actions for bulk update
    actions = ['mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected orders as cancelled"


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)


admin.site.register(Product, ProductAdmin)

admin.site.register(Category, CategoryAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
