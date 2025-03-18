from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure email is unique
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False) 

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Name of the category

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)  # Product name
    short_description = models.CharField(max_length=255)  # Short description
    full_description = models.TextField()  # Full description
    image = models.ImageField(upload_to='product_images/')  # Product image
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price
    available_quantity = models.PositiveIntegerField()  # Available quantity
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Sale price (optional)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)  # Category
    
    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='carts')  # Owner of the cart
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='carts')  # Product added
    quantity = models.PositiveIntegerField(default=1)  # Number of items in the cart
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Auto-calculated total price
    is_checked_out = models.BooleanField(default=False)  # Status of cart (checked out or not)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when cart item was added
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when cart was updated

    def save(self, *args, **kwargs):
        """Auto-calculate total price before saving."""
        if self.product and self.quantity:
            # If sale price exists, use it; otherwise, fall back to regular price
            self.total_price = self.quantity * (self.product.sale_price if self.product.sale_price else self.product.price)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart {self.id} - {self.user.username} - {self.product.name}"



class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Card Payment'),
        ('upi', 'UPI Payment'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total order cost
    created_at = models.DateTimeField(auto_now_add=True)  # Order creation time
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered'),('cancelled', 'Cancelled')],
        default='pending'
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod') 

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at checkout

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
