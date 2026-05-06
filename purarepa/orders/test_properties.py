"""Property-based tests for the orders app serializers.

Validates: Requirements 5.7, 6.1
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from unittest.mock import MagicMock

from orders.serializers import OrderCreateSerializer


def _make_mock_request():
    """Return a mock request with an authenticated user."""
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_request = MagicMock()
    mock_request.user = mock_user
    return mock_request


@pytest.mark.django_db
@given(address=st.one_of(st.just(""), st.text(alphabet=" \t\n", min_size=1)))
@settings(max_examples=100)
def test_order_serializer_rejects_blank_address(address):
    """Propiedad 4: El serializer rechaza pedidos con dirección vacía.

    Para cualquier delivery_address que sea cadena vacía o compuesta solo de
    espacios en blanco, el serializer debe rechazar la creación y devolver un
    error de validación en el campo 'delivery_address'.

    Validates: Requirements 5.7, 6.1
    """
    data = {
        "payment_method": "MANUAL",
        "delivery_address": address,
        "items": [],
    }
    serializer = OrderCreateSerializer(
        data=data,
        context={"request": _make_mock_request()},
    )
    assert not serializer.is_valid(), (
        f"El serializer debería rechazar delivery_address={address!r}, "
        f"pero lo aceptó."
    )
    assert "delivery_address" in serializer.errors, (
        f"Se esperaba 'delivery_address' en los errores, "
        f"pero se obtuvieron: {serializer.errors}"
    )
