"""Models for the products app."""

from django.db import models


class Product(models.Model):
    """Represents a product (arepa) available in the store."""

    TYPES = (
        ('TRADICIONAL', 'Tradicional'),
        ('QUESO', 'Queso'),
        ('CHOCLO', 'Choclo'),
        ('RELLENA', 'Rellena'),
        ('MORADA', 'Maíz Morado'),
    )

    name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=20, choices=TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='arepas/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Product."""

        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self) -> str:
        return str(self.name)
