"""URL configuration for the reports app."""

from django.urls import path

from .views import ClientReportView, DashboardView, SalesReportView

urlpatterns = [
    path('clients/', ClientReportView.as_view(), name='report-clients'),
    path('sales/', SalesReportView.as_view(), name='report-sales'),
    path('dashboard/', DashboardView.as_view(), name='report-dashboard'),
]
