"""Views for the orders app."""
# pylint: disable=no-member

import mercadopago
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from .models import Order, PaymentProof
from .serializers import (
    OrderCreateSerializer, OrderStatusSerializer,
    PaymentProofSerializer, PaymentProofAdminSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """ViewSet for listing, creating and managing orders."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use OrderCreateSerializer for creation, OrderStatusSerializer for updates."""
        if self.action in ('update', 'partial_update'):
            return OrderStatusSerializer
        return OrderCreateSerializer

    def get_queryset(self):
        """Return all orders for admins, or only the user's own orders."""
        if getattr(self.request.user, 'role', '') != 'ADMIN' and not self.request.user.is_staff:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_proof(self, request, pk=None):  # pylint: disable=unused-argument
        """Upload a payment proof for a manual-payment order."""
        order = self.get_object()
        if order.payment_method != 'MANUAL':
            return Response({"error": "No habilitado"}, status=400)
        if PaymentProof.objects.filter(order=order).exists():
            return Response({"error": "Ya existe comprobante"}, status=400)
        ser = PaymentProofSerializer(data=request.data)
        if ser.is_valid():
            PaymentProof.objects.create(order=order, **ser.validated_data)
            return Response({"message": "Subido"}, status=201)
        return Response(ser.errors, status=400)


class ProofAdminViewSet(viewsets.GenericViewSet,
                        viewsets.mixins.ListModelMixin,
                        viewsets.mixins.UpdateModelMixin):
    """ViewSet for admins to list and verify payment proofs."""

    permission_classes = [IsAdminRole]
    serializer_class = PaymentProofAdminSerializer
    queryset = PaymentProof.objects.all().order_by('-uploaded_at')

    @action(detail=True, methods=['patch'])
    def verify(self, request, pk=None):
        """Approve or reject a payment proof."""
        proof = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ('APPROVED', 'REJECTED'):
            return Response({"error": "Estado inválido"}, status=400)
        proof.status = new_status
        proof.save()
        if new_status == 'APPROVED':
            proof.order.status = 'PAID'
            proof.order.save()
        return Response(PaymentProofAdminSerializer(proof).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mp_checkout(request, order_id):
    """Create a MercadoPago preference and return the checkout URL."""
    order = Order.objects.get(id=order_id, user=request.user)
    if order.status != 'PENDING' or order.payment_method != 'GATEWAY':
        return Response({"error": "Orden no apta"}, status=400)
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
    resp = sdk.preference().create({
        "items": [{
            "title": f"Purarepa #{order.id}",
            "quantity": 1,
            "unit_price": float(order.total),
            "currency_id": "COP",
        }],
        "external_reference": str(order.id),
        "back_urls": {
            "success": f"{settings.FRONTEND_URL}/payment/success",
            "failure": f"{settings.FRONTEND_URL}/payment/failure",
            "pending": f"{settings.FRONTEND_URL}/payment/pending",
        },
        "auto_return": "approved",
    })
    order.mp_preference_id = resp["response"]["id"]
    order.save()
    return Response({"checkout_url": resp["response"]["init_point"]})


@api_view(['POST'])
@permission_classes([AllowAny])
def mp_webhook(request):
    """Handle MercadoPago payment webhook notifications."""
    if request.data.get('type') == 'payment':
        pid = request.data.get('data', {}).get('id')
        pay = mercadopago.SDK(settings.MP_ACCESS_TOKEN).payment().get(pid)
        pay_status = pay["response"]["status"]
        order_id = pay["response"]["external_reference"]
        if pay_status == 'approved':
            Order.objects.filter(id=order_id).update(status='PAID')
        elif pay_status in ['rejected', 'cancelled']:
            Order.objects.filter(id=order_id).update(status='CANCELLED')
    return Response({"message": "OK"})
