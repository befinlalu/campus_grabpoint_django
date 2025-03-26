from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, Category, Product, Order, OrderItem, PrintOrder
from .models import CustomUser, Category, Product, Order, OrderItem, PrintOrder, PrintOrderFile


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

from django.utils.html import format_html, mark_safe
from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import PrintOrder, PrintOrderFile


class PrintOrderFileInline(admin.TabularInline):
    model = PrintOrderFile
    extra = 0  # Shows existing files without extra empty forms

class PrintOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total_price", "status", "payment_status", "created_at", "files"]
    list_filter = ["status", "payment_status", "created_at"]
    search_fields = ["user__username", "status", "payment_status"]
    inlines = [PrintOrderFileInline]  # Show related files inside order details

    actions = ["mark_as_shipped", "mark_as_delivered", "mark_as_cancelled"]

    fieldsets = (
        ("Order Information", {"fields": ("user", "total_price", "status", "payment_status","transaction_id", "created_at")}),
        ("Print Preferences", {"fields": ("paper_size", "color_mode", "print_sides", "binding_option", "urgency", "additional_notes")}),
        ("Uploaded Files", {"fields": ("file_list",)}),  # Custom field to display files
    )

    readonly_fields = ("file_list", "created_at")  # Prevent modification of file list

    def files(self, obj):
        """Displays associated files as clickable links in the order list view."""
        file_links = [
            f'<a href="{file.file.url}" target="_blank">{file.file.name.split("/")[-1]}</a>'
            for file in obj.files.all()
        ]
        return mark_safe("<br>".join(file_links)) if file_links else "No files uploaded"

    files.short_description = "Files"

    def file_list(self, obj):
        """Displays files in the detailed order view."""
        return self.files(obj)

    file_list.short_description = "Uploaded Files"

    def save_model(self, request, obj, form, change):
        if change:
            original = PrintOrder.objects.get(pk=obj.pk)
            if original.status != obj.status:
                self.send_status_email(obj)
        super().save_model(request, obj, form, change)

    def send_status_email(self, order):
        file_links = "\n".join(
            [f"- {settings.SITE_URL}{file.file.url}" for file in order.files.all()]
        )
        subject = f"Print Order #{order.id} Status Update"
        message = f"""
        Dear {order.user.username},

        Your print order status has been updated to: {order.status}.

        Order Details:
        - Paper Size: {order.paper_size}
        - Color Mode: {order.color_mode}
        - Print Sides: {order.print_sides}
        - Binding Option: {order.binding_option}
        - Urgency: {order.urgency}
        - Additional Notes: {order.additional_notes or 'None'}
        - Payment Status: {order.payment_status}

        Files:
        {file_links if file_links else "No files uploaded"}

        Thank you for using our service!
        """
        recipient_list = [order.user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    def mark_as_shipped(self, request, queryset):
        queryset.update(status="printed")
        for order in queryset:
            self.send_status_email(order)
    mark_as_shipped.short_description = "Mark selected orders as Printed"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status="delivered")
        for order in queryset:
            self.send_status_email(order)
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status="cancelled")
        for order in queryset:
            self.send_status_email(order)
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"






admin.site.register(PrintOrder, PrintOrderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CustomUser, CustomUserAdmin)



