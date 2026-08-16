from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductCreateAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/inventory/', views.ProductChangeAPIView.as_view(), name='product-change'),
    path('products/<int:pk>/history/', views.ProductHistoryAPIView.as_view(), name='product-history'),
]