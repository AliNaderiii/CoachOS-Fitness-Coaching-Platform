"""Core app URL patterns."""

from django.urls import include, path

from apps.core.views import MetaView

urlpatterns = [
    path("meta", MetaView.as_view(), name="meta"),
    # Phase 05 Identity, Tenancy & Roles
    path("auth/", include("apps.identity.urls")),
    path("organizations/", include("apps.organizations.urls")),
    # Phase 06 Exercise Library & Training Programs
    path("", include("apps.exercises.urls")),
    path("", include("apps.programs.urls")),
]
