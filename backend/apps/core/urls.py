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
    # Phase 07 Athlete Execution and Progress
    path("", include("apps.execution.urls")),
    # Phase 08 Communication and Notifications
    path("", include("apps.communication.urls")),
    # Phase 10 Organization Billing and Coach Monetization
    path("", include("apps.billing.urls")),
    # Phase 11 Governed AI Copilot
    path("", include("apps.copilot.urls")),
    # Phase 12 Durable Offline and Integrations
    path("integrations/", include("apps.integrations.urls")),
]
