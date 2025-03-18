from django.urls import path
from .views import UserRegistrationView, CustomTokenObtainPairView, LogoutView, ProductListView, CartView,AddToCartView,CheckoutView,UserOrdersView

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('cart/', CartView.as_view(), name='cart'),  # Added cart endpoint
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', UserOrdersView.as_view(), name='user-orders'),

]
