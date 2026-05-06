"""Property-based integration tests for the orders app.

These tests use real DB objects (Product, User, Order) to verify
backend invariants across many generated inputs.

Validates: Requirement 6.2, 6.3, 6.4
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.contrib.auth import get_user_model
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from rest_framework import serializers

from orders.serializers import OrderCreateSerializer
from products.models import Product

User = get_user_model()


def _make_mock_request(user):
    """Return a mock request with the given authenticated user."""
    mock_request = MagicMock()
    mock_request.user = user
    return mock_request


@pytest.mark.django_db
@given(
    price=st.decimals(
        min_value=Decimal("100"),
        max_value=Decimal("100000"),
        places=2,
        allow_nan=False,
        allow_infinity=False,
    )
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
def test_order_item_preserves_unit_price(price):
    """Propiedad 5: La creación de Order preserva los precios unitarios vigentes.

    Para cualquier Order creado exitosamente, el unit_price de cada OrderItem
    debe ser igual al price del Product correspondiente en el momento de la
    creación, independientemente de cambios posteriores al precio del producto.

    Validates: Requirement 6.2
    """
    # Use a unique suffix per test invocation to avoid UNIQUE constraint collisions
    unique_suffix = uuid.uuid4().hex[:8]

    # Create a real user in the DB
    user = User.objects.create_user(
        username=f"u_{unique_suffix}",
        password="testpass123",
    )

    # Create a real product with the generated price and sufficient stock
    product = Product.objects.create(
        name=f"Arepa {unique_suffix}",
        product_type="TRADICIONAL",
        description="Arepa de prueba para property test",
        price=price,
        stock=10,
        is_active=True,
    )

    # Build the serializer with a real user in the request context
    data = {
        "payment_method": "MANUAL",
        "delivery_address": "Calle 123 # 45-67, Bogotá",
        "items": [{"product_id": product.id, "quantity": 1}],
    }
    serializer = OrderCreateSerializer(
        data=data,
        context={"request": _make_mock_request(user)},
    )

    assert serializer.is_valid(), (
        f"El serializer debería ser válido, pero tiene errores: {serializer.errors}"
    )

    order = serializer.save()

    # Verify that the OrderItem's unit_price matches the product's price at creation time
    order_item = order.items.first()
    assert order_item is not None, "El Order debería tener al menos un OrderItem"
    assert order_item.unit_price == price, (
        f"Se esperaba unit_price={price}, pero se obtuvo {order_item.unit_price}"
    )


@pytest.mark.django_db
@given(
    initial_stock=st.integers(min_value=1, max_value=100),
    quantity=st.integers(min_value=1, max_value=100),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
def test_order_stock_decrement_atomic(initial_stock, quantity):
    """Propiedad 6: La creación de Order decrementa el stock atómicamente.

    Para cualquier Order creado exitosamente con K ítems, el stock de cada
    producto incluido debe decrementarse exactamente en la cantidad solicitada.
    Si algún producto tiene stock insuficiente, ningún stock debe modificarse
    (transacción atómica).

    Validates: Requirements 6.3, 6.4
    """
    unique_suffix = uuid.uuid4().hex[:8]

    # Create a real user in the DB
    user = User.objects.create_user(
        username=f"u_{unique_suffix}",
        password="testpass123",
    )

    # Create a real product with the generated initial_stock
    product = Product.objects.create(
        name=f"Arepa {unique_suffix}",
        product_type="TRADICIONAL",
        description="Arepa de prueba para property test de stock",
        price=Decimal("5000.00"),
        stock=initial_stock,
        is_active=True,
    )

    data = {
        "payment_method": "MANUAL",
        "delivery_address": "Calle 123 # 45-67, Bogotá",
        "items": [{"product_id": product.id, "quantity": quantity}],
    }
    serializer = OrderCreateSerializer(
        data=data,
        context={"request": _make_mock_request(user)},
    )

    assert serializer.is_valid(), (
        f"El serializer debería ser válido en is_valid(), pero tiene errores: {serializer.errors}"
    )

    if quantity <= initial_stock:
        # Sufficient stock: order should succeed and stock should decrement
        order = serializer.save()
        product.refresh_from_db()
        assert product.stock == initial_stock - quantity, (
            f"Se esperaba stock={initial_stock - quantity}, "
            f"pero se obtuvo {product.stock} "
            f"(initial_stock={initial_stock}, quantity={quantity})"
        )
        assert order is not None
    else:
        # Insufficient stock: ValidationError must be raised and stock must not change
        with pytest.raises(serializers.ValidationError):
            serializer.save()
        product.refresh_from_db()
        assert product.stock == initial_stock, (
            f"El stock no debería cambiar cuando quantity > initial_stock, "
            f"pero cambió de {initial_stock} a {product.stock} "
            f"(quantity={quantity})"
        )
