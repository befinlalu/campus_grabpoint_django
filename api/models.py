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


class OrderAddress(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='order_address')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    registration_no = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    note = models.TextField(blank=True, null=True)  # Optional field for extra notes

    def __str__(self):
        return f"Address for Order {self.order.id}"

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Card Payment'),
        ('upi', 'UPI Payment'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total order cost
    created_at = models.DateTimeField(auto_now_add=True)  # Order creation time
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
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


class PrintOrder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='print_orders')
    paper_size = models.CharField(max_length=10, choices=[("A4", "A4"), ("A3", "A3"), ("letter", "Letter")])
    color_mode = models.CharField(max_length=12, choices=[("color", "Color"), ("black/white", "Black & White")])
    print_sides = models.CharField(max_length=10, choices=[("single", "Single"), ("double", "Double")])
    binding_option = models.CharField(max_length=10, choices=[("staples", "Staples"), ("spiral", "Spiral")])
    urgency = models.CharField(max_length=10, choices=[("standard", "Standard"), ("express", "Express")])
    additional_notes = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pending"), ("printed", "Printed"),
        ("delivered", "Delivered"), ("cancelled", "Cancelled")
    ], default="pending")
    payment_status = models.CharField(max_length=20, choices=[("cod", "Cash on Delivery"), ("card", "Card Payment"), ("upi", "UPI Payment")], default="cod")

    def __str__(self):
        return f"Print Order {self.id} - {self.user.username}"

class PrintOrderFile(models.Model):
    print_order = models.ForeignKey(PrintOrder, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="print_orders/")  # Stores each file separately

    def __str__(self):
        return f"File for Order {self.print_order.id}"


class Rating(models.Model):
    RATING_CHOICES = [
        (1, 'Not Useful'),
        (2, 'Bad'),
        (3, 'Poor'),
        (4, 'Good'),
        (5, 'Very Good')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)  # Required rating field (1-5)
    title = models.CharField(max_length=50, blank=True)  # Auto-filled based on rating
    description = models.TextField(blank=True, null=True)  # Optional review
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def save(self, *args, **kwargs):
        """Auto-assign title based on rating value."""
        self.title = dict(self.RATING_CHOICES).get(self.rating, 'Unknown')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.user.username} ({self.rating})"