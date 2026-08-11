"""Core app URL patterns."""

from django.urls import path

from apps.core.views import MetaView

urlpatterns = [
    path("meta", MetaView.as_view(), name="meta"),
]
