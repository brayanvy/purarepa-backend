"""Integration tests for the orders app using Django REST Framework's APIClient.

These tests hit real API endpoints to verify authentication, validation,
stock management, and price preservation behaviour.

Validates: Requirements 2.1, 5.7, 6.1, 6.2, 6.3, 6.4
"""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from products.models import Product

User = get_user_model()

PRODUCTS_URL = "/api/products/"
ORDERS_URL = "/api/orders/"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username="testuser", password="testpass123"):
    """Create and return a regular user."""
    return User.objects.create_user(username=username, password=password)


def make_product(name="Arepa Test", price="5000.00", stock=10):
    """Create and return a Product with the given attributes."""
    return Product.objects.create(
        name=name,
        product_type="TRADICIONAL",
        description="Arepa de prueba",
        price=Decimal(price),
        stock=stock,
        is_active=True,
    )


def order_payload(product, quantity=1, address="Calle 123 # 45-67, Bogotá"):
    """Return a valid order creation payload."""
    return {
        "payment_method": "MANUAL",
        "delivery_address": address,
        "items": [{"product_id": product.id, "quantity": quantity}],
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_products_public_access():
    """GET /api/products/ without a token must return 200.

    Validates: Requirement 2.1
    """
    client = APIClient()
    response = client.get(PRODUCTS_URL)
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_requires_auth():
    """POST /api/orders/ without a token must return 401.

    Validates: Requirement 5.7
    """
    client = APIClient()
    product = make_product()
    response = client.post(ORDERS_URL, order_payload(product), format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_order_empty_address_rejected():
    """POST /api/orders/ with delivery_address="" must return 400.

    Validates: Requirement 6.1
    """
    client = APIClient()
    user = make_user()
    client.force_authenticate(user=user)

    product = make_product()
    payload = order_payload(product, address="")
    response = client.post(ORDERS_URL, payload, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_order_stock_decrement():
    """Creating an Order must decrement the product's stock by the ordered quantity.

    Validates: Requirement 6.3
    """
    client = APIClient()
    user = make_user()
    client.force_authenticate(user=user)

    initial_stock = 10
    quantity = 3
    product = make_product(stock=initial_stock)

    response = client.post(ORDERS_URL, order_payload(product, quantity=quantity), format="json")

    assert response.status_code == 201

    product.refresh_from_db()
    assert product.stock == initial_stock - quantity


@pytest.mark.django_db
def test_order_insufficient_stock():
    """POST /api/orders/ with quantity > stock must return 400 and leave stock unchanged.

    Validates: Requirement 6.4
    """
    client = APIClient()
    user = make_user()
    client.force_authenticate(user=user)

    initial_stock = 2
    product = make_product(stock=initial_stock)

    # Request more than available
    response = client.post(ORDERS_URL, order_payload(product, quantity=5), format="json")

    assert response.status_code == 400

    product.refresh_from_db()
    assert product.stock == initial_stock


@pytest.mark.django_db
def test_order_preserves_unit_price():
    """The unit_price in OrderItem must match the product's price at time of purchase.

    Validates: Requirement 6.2
    """
    client = APIClient()
    user = make_user()
    client.force_authenticate(user=user)

    price = Decimal("7500.00")
    product = make_product(price=str(price))

    response = client.post(ORDERS_URL, order_payload(product), format="json")

    assert response.status_code == 201

    order_id = response.data["id"]
    order = Order.objects.get(id=order_id)
    item = order.items.first()

    assert item is not None
    assert item.unit_price == price
