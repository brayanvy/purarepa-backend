"""Pytest configuration for the purarepa backend."""

import django
from django.conf import settings


def pytest_configure():
    """Configure Django settings for pytest."""
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
