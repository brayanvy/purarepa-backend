from django.contrib import admin
from .models import Order, OrderItem, PaymentProof


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'salt_preference')
    fields = ('product', 'quantity', 'unit_price', 'salt_preference')


class PaymentProofInline(admin.StackedInline):
    model = PaymentProof
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'payment_method', 'observacion', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'user__email', 'mp_preference_id', 'observacion')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Información del pedido', {
            'fields': ('user', 'status', 'payment_method', 'total', 'created_at'),
        }),
        ('Entrega', {
            'fields': ('delivery_address', 'observacion'),
        }),
        ('Pagos', {
            'fields': ('mp_preference_id',),
            'classes': ('collapse',),
        }),
    )
    inlines = [OrderItemInline, PaymentProofInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'salt_preference')
    search_fields = ('order__id', 'product__name')


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'uploaded_at')
    list_filter = ('status',)
    readonly_fields = ('uploaded_at',)
