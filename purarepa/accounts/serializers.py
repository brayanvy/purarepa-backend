"""Serializers for the accounts app."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("username", "email", "password", "phone")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            phone=validated_data.get("phone", ""),
            role="CLIENT",
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for reading the current user's profile."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "phone", "role")
        read_only_fields = fields
