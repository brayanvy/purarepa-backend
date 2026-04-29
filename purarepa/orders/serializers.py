"""Serializers for the orders app."""
# pylint: disable=no-member

from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from products.models import Product

from .models import Order, OrderItem, PaymentProof


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for reading order items."""

    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'unit_price')


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an order with its items."""

    items = serializers.ListField(child=serializers.DictField(), write_only=True)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'payment_method', 'items', 'order_items', 'total', 'status', 'created_at')
        read_only_fields = ('id', 'total', 'status', 'created_at', 'order_items')

    @transaction.atomic
    def create(self, validated_data):
        """Create an order, update stock, and calculate total."""
        items = validated_data.pop('items')
        order = Order.objects.create(
            user=self.context['request'].user,
            total=Decimal('0.00'),
            **validated_data,
        )
        total = Decimal('0.00')
        for item in items:
            prod = Product.objects.select_for_update().get(id=item['product_id'])
            if prod.stock < item['quantity']:
                raise serializers.ValidationError(
                    f"Stock insuficiente: {prod.name}"
                )
            prod.stock -= item['quantity']
            prod.save()
            OrderItem.objects.create(
                order=order,
                product=prod,
                quantity=item['quantity'],
                unit_price=prod.price,
            )
            total += prod.price * item['quantity']
        order.total = total
        order.save()
        return order


class PaymentProofSerializer(serializers.ModelSerializer):
    """Serializer for uploading a payment proof file."""

    class Meta:
        model = PaymentProof
        fields = ('file',)


class PaymentProofAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin review of payment proofs."""

    class Meta:
        model = PaymentProof
        fields = ('id', 'order', 'file', 'status', 'uploaded_at')
        read_only_fields = ('id', 'order', 'file', 'uploaded_at')
