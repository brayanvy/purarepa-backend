"""Models for the orders app."""

from django.conf import settings
from django.db import models


class Order(models.Model):
    """Represents a customer order."""

    STATUS = (
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('SHIPPED', 'Enviado'),
        ('CANCELLED', 'Cancelado'),
    )
    PAYMENT = (
        ('GATEWAY', 'Pasarela'),
        ('MANUAL', 'Comprobante'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    payment_method = models.CharField(max_length=10, choices=PAYMENT)
    delivery_address = models.TextField(blank=True, default='')
    mp_preference_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Order."""

        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self) -> str:
        return f"Order #{self.pk} - {self.user}"


class OrderItem(models.Model):
    """Represents a single product line within an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        """Meta options for OrderItem."""

        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product} (Order #{self.order.pk})"


class PaymentProof(models.Model):
    """Stores a payment proof file uploaded by the user."""

    STATUS = (
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='proof')
    file = models.FileField(upload_to='proofs/')
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for PaymentProof."""

        verbose_name = 'Payment Proof'
        verbose_name_plural = 'Payment Proofs'

    def __str__(self) -> str:
        return f"Proof for Order #{self.order.pk} - {self.status}"
