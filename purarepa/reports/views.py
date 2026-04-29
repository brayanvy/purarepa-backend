"""Views for the reports app."""
# pylint: disable=no-member

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from orders.models import Order, OrderItem


class ClientReportView(APIView):
    """Returns a summary of clients and their order activity."""

    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """List all clients with their total orders and revenue."""
        clients = (
            User.objects
            .filter(role='CLIENT')
            .annotate(
                order_count=Count('orders'),
                order_total=Sum('orders__total'),
            )
        )
        data = [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'orders': u.order_count,
                'total': float(u.order_total or 0),
            }
            for u in clients
        ]
        return Response(data)


class SalesReportView(APIView):
    """Returns aggregated sales figures for paid orders."""

    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """Return total revenue and number of paid orders."""
        qs = Order.objects.filter(status='PAID')
        return Response({
            'total_revenue': float(
                qs.aggregate(Sum('total'))['total__sum'] or 0
            ),
            'orders': qs.count(),
        })


class DashboardView(APIView):
    """Returns dashboard data: top products and monthly sales."""

    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """Return top 5 products by units sold and monthly revenue breakdown."""
        top_products = list(
            OrderItem.objects
            .filter(order__status='PAID')
            .values('product__name')
            .annotate(sold=Sum('quantity'))
            .order_by('-sold')[:5]
        )
        monthly_sales = list(
            Order.objects
            .filter(status='PAID')
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(revenue=Sum('total'))
            .order_by('month')
        )
        return Response({
            'top_products': top_products,
            'monthly_sales': monthly_sales,
        })
