from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer,OrderSerializer
from .models import Product, Cart,Order, OrderItem
from .serializers import ProductSerializer, CartSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated




# Product List View
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name', 'category__name']  # Fields to filter on
    ordering_fields = ['price', 'name']  # Allow sorting by price or name
    ordering = ['name']  # Default ordering by name


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
        """Creates an order from the cart and clears the cart."""
        cart_items = Cart.objects.filter(user=request.user, is_checked_out=False)

        if not cart_items.exists():
            return Response({"error": "Cart is empty!"}, status=status.HTTP_400_BAD_REQUEST)

        # Get payment status from request
        payment_status = request.data.get("payment_status")

        # Validate payment status
        valid_payment_choices = [choice[0] for choice in Order.PAYMENT_CHOICES]
        if payment_status not in valid_payment_choices:
            return Response(
                {"error": f"Invalid payment status! Choose from {valid_payment_choices}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate total price
        total_price = sum(item.total_price for item in cart_items)

        # Create the order with payment status
        order = Order.objects.create(user=request.user, total_price=total_price, payment_status=payment_status)

        # Create order items
        order_items = [
            OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.total_price)
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # Mark cart items as checked out
        cart_items.update(is_checked_out=True)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve orders of the authenticated user."""
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Get user's orders sorted by latest
        serializer = OrderSerializer(user_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

