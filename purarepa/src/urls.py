"""URL configuration for the purarepa project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from orders.views import mp_checkout, mp_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/orders/payment/checkout/<int:order_id>/', mp_checkout, name='mp_checkout'),
    path('api/orders/payment/webhook/', mp_webhook, name='mp_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
