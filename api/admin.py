from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, Category, Product, Order, OrderItem, PrintOrder


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'phone_number', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'full_name', 'phone_number')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'full_name', 'phone_number', 'is_verified', 'is_active')
        }),
    )
    filter_horizontal = ('groups', 'user_permissions',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_description', 'price', 'available_quantity', 'sale_price', 'category')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['user__username', 'status', 'payment_status']
    inlines = [OrderItemInline]

    actions = ['mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def save_model(self, request, obj, form, change):
        if change:
            original = Order.objects.get(pk=obj.pk)
            if original.status != obj.status:
                self.send_status_email(obj)
        super().save_model(request, obj, form, change)

    def send_status_email(self, order):
        subject = f"Order #{order.id} Status Update"
        message = f"Dear {order.user.username},\n\nYour order status has been updated to: {order.status}.\n\nThank you!"
        recipient_list = [order.user.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        for order in queryset:
            self.send_status_email(order)
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        for order in queryset:
            self.send_status_email(order)
    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        for order in queryset:
            self.send_status_email(order)
    mark_as_cancelled.short_description = "Mark selected orders as cancelled"


class PrintOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total_price", "status", "payment_status", "created_at"]
    list_filter = ["status", "payment_status", "created_at"]
    search_fields = ["user__username", "status", "payment_status"]

    actions = ["mark_as_shipped", "mark_as_delivered", "mark_as_cancelled"]

    def save_model(self, request, obj, form, change):
        if change:
            original = PrintOrder.objects.get(pk=obj.pk)
            if original.status != obj.status:
                self.send_status_email(obj)
        super().save_model(request, obj, form, change)

    def send_status_email(self, order):
        subject = f"Print Order #{order.id} Status Update"
        message = f"Dear {order.user.username},\n\nYour print order status has been updated to: {order.status}.\n\nThank you!"
        recipient_list = [order.user.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    def mark_as_shipped(self, request, queryset):
        queryset.update(status="shipped")
        for order in queryset:
            self.send_status_email(order)
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status="delivered")
        for order in queryset:
            self.send_status_email(order)
    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status="cancelled")
        for order in queryset:
            self.send_status_email(order)
    mark_as_cancelled.short_description = "Mark selected orders as cancelled"


admin.site.register(PrintOrder, PrintOrderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CustomUser, CustomUserAdmin)


