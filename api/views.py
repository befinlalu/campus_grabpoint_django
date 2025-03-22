from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer,RatingSerializer, CustomTokenObtainPairSerializer,OrderSerializer,CategorySerializer,PrintOrderSerializer,OrderAddressSerializer,ForgotPasswordSerializer,UserSerializer
from .models import Product, Cart,Order, OrderItem, Category,PrintOrder,PrintOrderFile,Rating,OrderAddress
from .serializers import ProductSerializer, CartSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count
import django_filters
from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model


User = get_user_model()


# User Registration View
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to register

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

    def get(self, request, *args, **kwargs):
        user = request.user  # Get the logged-in user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class ForgotPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            new_password = serializer.validated_data["new_password"]
            user.password = make_password(new_password)
            user.save()

            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Custom Token Obtain View (JWT Login)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Logout View
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # You can add logic to blacklist the token here if needed
        return Response({"message": "Logged out successfully!"}, status=status.HTTP_200_OK)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all cart items for the logged-in user along with total price."""
        cart_items = Cart.objects.filter(user=request.user, is_checked_out=False)
        serializer = CartSerializer(cart_items, many=True, context={'request': request})

        total_cart_price = sum(item.total_price for item in cart_items)  # Calculate total price

        return Response({
            "cart_items": serializer.data,
            "total_cart_price": total_cart_price
        }, status=status.HTTP_200_OK)

# Add to Cart View
class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Add a product to the cart or update its quantity if it already exists."""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        product = get_object_or_404(Product, id=product_id)  # Ensure product exists

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            is_checked_out=False,  # Ensure we're modifying an active cart
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += int(quantity)  # Update quantity
            cart_item.save()

        return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Creates an order from the cart and clears the cart, including address."""
        cart_items = Cart.objects.filter(user=request.user, is_checked_out=False)

        if not cart_items.exists():
            return Response({"error": "Cart is empty!"}, status=status.HTTP_400_BAD_REQUEST)

        # Get payment status and address details
        payment_status = request.data.get("payment_status")
        address_data = request.data.get("order_address")

        # Validate payment status
        valid_payment_choices = [choice[0] for choice in Order.PAYMENT_CHOICES]
        if payment_status not in valid_payment_choices:
            return Response(
                {"error": f"Invalid payment status! Choose from {valid_payment_choices}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate address data
        if not address_data:
            return Response({"error": "Order address is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price
        total_price = sum(item.total_price for item in cart_items)

        # Create the order
        order = Order.objects.create(user=request.user, total_price=total_price, payment_status=payment_status)

        # Create the order address
        OrderAddress.objects.create(order=order, **address_data)

        # Create order items
        order_items = [
            OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.total_price)
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # Mark cart items as checked out
        cart_items.update(is_checked_out=True)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class ProductFilter(django_filters.FilterSet):
    category_id = django_filters.BaseInFilter(field_name="category_id", lookup_expr="in")  # Allow multiple values

    class Meta:
        model = Product
        fields = ['category_id']

# Product List View with Multi-Category Filtering
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProductFilter  # Use the custom filter
    search_fields = ['name', 'category__name']  # Search by product name or category name
    ordering_fields = ['price', 'name']
    ordering = ['name']  # Default ordering

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'  # The URL will use 'id' to fetch a product

class ProductRatingListView(generics.ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        """Get all ratings for a specific product."""
        product_id = self.kwargs['product_id']
        return Rating.objects.filter(product_id=product_id)

class RatingCreateView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated] 

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PrintOrderCreateView(generics.CreateAPIView):
    queryset = PrintOrder.objects.all()
    serializer_class = PrintOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print_order = serializer.save(user=self.request.user)  # Assign user
        files = self.request.FILES.getlist('files')  # Get multiple files

        for file in files:
            PrintOrderFile.objects.create(print_order=print_order, file=file)

from rest_framework import generics, permissions
from .models import PrintOrder
from .serializers import PrintOrderSerializer

class UserPrintOrderListView(generics.ListAPIView):
    serializer_class = PrintOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve only the print orders of the logged-in user"""
        return PrintOrder.objects.filter(user=self.request.user)


class CartDeleteView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Ensure users can only delete their own cart items."""
        return Cart.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        cart_item_id = kwargs.get('pk')  # Get cart item ID from URL
        cart_item = self.get_queryset().filter(id=cart_item_id).first()

        if cart_item:
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

class ProductRatingSummaryView(APIView):
    def get(self, request, product_id):
        """Get the average rating and total number of ratings for a product."""
        ratings = Rating.objects.filter(product_id=product_id)
        
        if not ratings.exists():
            return Response({"message": "No ratings found for this product."}, status=status.HTTP_404_NOT_FOUND)
        
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        total_ratings = ratings.count()

        return Response({
            "product_id": product_id,
            "average_rating": round(avg_rating, 1),  # Rounded to 1 decimal place
            "total_ratings": total_ratings
        })

class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, cart_id):
        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        new_quantity = request.data.get('quantity')
        if new_quantity is None or int(new_quantity) < 1:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = int(new_quantity)
        cart_item.save()
        return Response(CartSerializer(cart_item).data, status=status.HTTP_200_OK)

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve orders of the authenticated user including address details."""
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(user_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
