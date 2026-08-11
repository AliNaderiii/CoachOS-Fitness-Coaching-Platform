"""
URL Configuration for CoachOS Fitness Coaching Platform.
"""

from django.urls import include, path

from apps.core.views import HealthzView, ReadyzView, custom_404_handler, custom_500_handler

urlpatterns = [
    # Safe Foundation Health Endpoints
    path("healthz", HealthzView.as_view(), name="healthz"),
    path("readyz", ReadyzView.as_view(), name="readyz"),
    # API v1 Namespace
    path("api/v1/", include("apps.core.urls")),
]

handler404 = custom_404_handler
handler500 = custom_500_handler
