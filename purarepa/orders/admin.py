from django.contrib import admin
from .models import Order, OrderItem, PaymentProof


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price',)


class PaymentProofInline(admin.StackedInline):
    model = PaymentProof
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'user__email', 'mp_preference_id')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline, PaymentProofInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price')
    search_fields = ('order__id', 'product__name')


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'uploaded_at')
    list_filter = ('status',)
    readonly_fields = ('uploaded_at',)
