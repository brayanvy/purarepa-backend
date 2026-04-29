"""Views for the products app."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and managing products.

    - Any authenticated user can list/retrieve (GET).
    - Only admins can create, update, or delete.
    """

    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all()
        if not self.request.user.is_staff and not getattr(self.request.user, 'role', '') == 'ADMIN':
            qs = qs.filter(is_active=True)
        return qs

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAdminUser()]
