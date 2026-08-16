from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductCreateAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/increase/', views.ProductIncreaseAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/decrease/', views.ProductDecreaseAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/history/', views.ProductHistoryAPIView.as_view(), name='product-list'),
]