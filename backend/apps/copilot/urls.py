from django.urls import path

from .views import (
    CopilotCapabilitiesView,
    CopilotOutputApproveView,
    CopilotOutputEditView,
    CopilotOutputRejectView,
    CopilotRunCancelView,
    CopilotRunDetailView,
    CopilotRunRegenerateView,
    CopilotRunReportView,
    CopilotRunsView,
    CopilotSourceDetailView,
)

urlpatterns = [
    path("copilot/capabilities", CopilotCapabilitiesView.as_view(), name="copilot-capabilities"),
    path("copilot/runs", CopilotRunsView.as_view(), name="copilot-runs"),
    path("copilot/runs/<str:run_id>", CopilotRunDetailView.as_view(), name="copilot-run-detail"),
    path(
        "copilot/runs/<str:run_id>/cancel",
        CopilotRunCancelView.as_view(),
        name="copilot-run-cancel",
    ),
    path(
        "copilot/runs/<str:run_id>/regenerate",
        CopilotRunRegenerateView.as_view(),
        name="copilot-run-regenerate",
    ),
    path(
        "copilot/runs/<str:run_id>/report",
        CopilotRunReportView.as_view(),
        name="copilot-run-report",
    ),
    path(
        "copilot/runs/<str:run_id>/output",
        CopilotOutputEditView.as_view(),
        name="copilot-output-edit",
    ),
    path(
        "copilot/runs/<str:run_id>/output/approve",
        CopilotOutputApproveView.as_view(),
        name="copilot-output-approve",
    ),
    path(
        "copilot/runs/<str:run_id>/output/reject",
        CopilotOutputRejectView.as_view(),
        name="copilot-output-reject",
    ),
    path(
        "copilot/runs/<str:run_id>/sources/<str:source_ref_id>",
        CopilotSourceDetailView.as_view(),
        name="copilot-source-detail",
    ),
]
