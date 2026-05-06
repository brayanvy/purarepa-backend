"""Unit tests for the orders app serializers.

Validates: Requirements 5.7, 6.1
"""

from unittest.mock import MagicMock

import pytest

from orders.serializers import OrderCreateSerializer


def _make_mock_request():
    """Return a mock request with an authenticated user."""
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_request = MagicMock()
    mock_request.user = mock_user
    return mock_request


def _make_serializer(delivery_address):
    """Build an OrderCreateSerializer with the given delivery_address."""
    data = {
        "payment_method": "MANUAL",
        "delivery_address": delivery_address,
        "items": [],
    }
    return OrderCreateSerializer(
        data=data,
        context={"request": _make_mock_request()},
    )


@pytest.mark.django_db
def test_order_empty_address_rejected():
    """delivery_address='' must be rejected by the serializer (→ 400).

    Validates: Requirements 5.7, 6.1
    """
    serializer = _make_serializer("")
    assert not serializer.is_valid()
    assert "delivery_address" in serializer.errors


@pytest.mark.django_db
def test_order_whitespace_address_rejected():
    """delivery_address='   ' must be rejected by the serializer (→ 400).

    Validates: Requirements 5.7, 6.1
    """
    serializer = _make_serializer("   ")
    assert not serializer.is_valid()
    assert "delivery_address" in serializer.errors


@pytest.mark.django_db
def test_order_valid_address_accepted():
    """A non-blank delivery_address must pass serializer validation.

    Validates: Requirements 5.7, 6.1
    """
    serializer = _make_serializer("Calle 123, Bogotá")
    # is_valid() may still be False due to empty items list, but the
    # delivery_address field itself must NOT appear in the errors.
    serializer.is_valid()
    assert "delivery_address" not in serializer.errors
