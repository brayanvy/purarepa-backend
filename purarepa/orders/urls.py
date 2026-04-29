"""URL configuration for the orders app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, ProofAdminViewSet

router = DefaultRouter()
router.register(r'admin/proofs', ProofAdminViewSet, basename='proof-admin')
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
