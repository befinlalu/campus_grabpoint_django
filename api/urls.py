from django.urls import path
from .views import UserRegistrationView, CustomTokenObtainPairView, LogoutView, ProductListView, CartView,AddToCartView,CheckoutView,UserOrdersView,CategoryListView,PrintOrderCreateView,UserPrintOrderListView,CartDeleteView
from .views import ProductDetailView,RatingCreateView,ProductRatingListView, ProductRatingSummaryView,UpdateCartQuantityView

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/', CartView.as_view(), name='cart'),  # Added cart endpoint
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', UserOrdersView.as_view(), name='user-orders'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path("print-orders/", PrintOrderCreateView.as_view(), name="print-order-create"),
    path('print-orders/view/', UserPrintOrderListView.as_view(), name='user-print-orders'),
    path('cart/remove/<int:pk>/', CartDeleteView.as_view(), name='cart-remove'),
    path('ratings/add/', RatingCreateView.as_view(), name='add-rating'),
    path('products/<int:product_id>/ratings/', ProductRatingListView.as_view(), name='product-ratings'),
     path('products/<int:product_id>/rating-summary/', ProductRatingSummaryView.as_view(), name='product-rating-summary'),
      path('cart/update/<int:cart_id>/', UpdateCartQuantityView.as_view(), name='update-cart-quantity'),
]
