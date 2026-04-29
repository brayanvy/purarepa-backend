"""Views for the accounts app."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserProfileSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Register a new client user."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Usuario creado correctamente."},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    """Return the current authenticated user's profile."""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)
