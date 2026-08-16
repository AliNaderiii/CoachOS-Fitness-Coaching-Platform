from django.urls import path

from .views import (
    BillingAdminDetailView,
    BillingAdminListCreateView,
    BillingWebhookView,
    BillingWorkspaceView,
    CheckoutSessionView,
    PlanListView,
    PortalSessionView,
    ReconcileView,
)

urlpatterns = [
    path("billing/plans", PlanListView.as_view(), name="billing-plans"),
    path(
        "billing/organizations/<str:org_id>/workspace",
        BillingWorkspaceView.as_view(),
        name="billing-workspace",
    ),
    path(
        "billing/organizations/<str:org_id>/checkout-sessions",
        CheckoutSessionView.as_view(),
        name="billing-checkout-session",
    ),
    path(
        "billing/organizations/<str:org_id>/portal-sessions",
        PortalSessionView.as_view(),
        name="billing-portal-session",
    ),
    path(
        "billing/organizations/<str:org_id>/admins",
        BillingAdminListCreateView.as_view(),
        name="billing-admins",
    ),
    path(
        "billing/organizations/<str:org_id>/admins/<str:assignment_id>",
        BillingAdminDetailView.as_view(),
        name="billing-admin-detail",
    ),
    path(
        "billing/organizations/<str:org_id>/reconcile",
        ReconcileView.as_view(),
        name="billing-reconcile",
    ),
    path("billing/webhooks/<str:provider>", BillingWebhookView.as_view(), name="billing-webhook"),
]
