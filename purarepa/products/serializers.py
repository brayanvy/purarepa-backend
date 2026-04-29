"""Serializers for the products app."""

from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model."""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'product_type', 'description',
            'price', 'stock', 'is_active', 'image', 'image_url',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'image_url', 'created_at', 'updated_at')

    def get_image_url(self, obj):
        """Return the absolute URL of the product image, or None if not set."""
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
