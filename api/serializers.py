from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import Cart, Product, Order, OrderItem,Category,PrintOrder,PrintOrderFile,Rating,OrderAddress


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()  # Get the user model dynamically
        fields = ['id', 'username', 'email', 'full_name'] 

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'full_name']  # Add full_name here

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', ''),
            full_name=validated_data.get('full_name', '')  # Handle full_name
        )
        return user

class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        username = data.get("username")
        email = data.get("email")

        # Check if user exists
        user = User.objects.filter(username=username, email=email).first()
        if not user:
            raise serializers.ValidationError("User with given username and email does not exist.")
        
        data["user"] = user  # Store user for use in view
        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Check if the user is verified before issuing a token
        if not user.is_verified:
            raise AuthenticationFailed("User is not verified. Please contact management.")

        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'  # Get all fields of category

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Include full category details

    class Meta:
        model = Product
        fields = '__all__'



class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=False
    )  # Make user optional, backend will set it
    product = ProductSerializer(read_only=True)  # Populated product details in response
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )  # Accept product_id in request
    quantity = serializers.IntegerField(min_value=1, required=True)  # Ensure valid quantity
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Auto-calculated

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'product_id', 'quantity', 'total_price']  # Include product_id for request

    def create(self, validated_data):
        """Ensure user is set and manage cart item updates."""
        user = self.context['request'].user  # Ensure user is set from

class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = ['first_name', 'last_name', 'registration_no', 'phone_number', 'email', 'note']

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()  # Show product name instead of ID

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)  # Include order items
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payment_status = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES)  # Allow payment status update
    transaction_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # Fix here
    order_address = OrderAddressSerializer()  # Include address details in response

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'payment_status', 'transaction_id', 'created_at', 'items', 'order_address']
        read_only_fields = ['user', 'total_price', 'status', 'created_at', 'items']

    def update(self, instance, validated_data):
        """Allow updating payment_status and transaction_id"""
        instance.payment_status = validated_data.get('payment_status', instance.payment_status)
        instance.transaction_id = validated_data.get('transaction_id', instance.transaction_id)
        instance.save()
        return instance




class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class PrintOrderFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintOrderFile
        fields = ["id", "file"]

class PrintOrderSerializer(serializers.ModelSerializer):
    files = PrintOrderFileSerializer(many=True, read_only=True)  # Handle multiple files

    class Meta:
        model = PrintOrder
        fields = [
            "id", "files", "paper_size", "color_mode", "print_sides",
            "binding_option", "urgency", "additional_notes",
            "total_price", "created_at", "status", "payment_status",
            "transaction_id"  # Added transaction_id
        ]
        read_only_fields = ["id", "created_at", "status"]




class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # ✅ Use full user details instead of just ID
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  

    class Meta:
        model = Rating
        fields = ['id', 'user', 'product', 'rating', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'title', 'created_at']  

    def create(self, validated_data):
        """Auto-assign user from request."""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)