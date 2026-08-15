from django.urls import path

from .views import (
    CoachAthleteAssignmentView,
    ProgramAssignmentView,
    ProgramCloneView,
    ProgramDetailView,
    ProgramListCreateView,
)

urlpatterns = [
    path("programs", ProgramListCreateView.as_view(), name="program-list-create"),
    path("programs/<str:program_id>", ProgramDetailView.as_view(), name="program-detail"),
    path("programs/<str:program_id>/clone", ProgramCloneView.as_view(), name="program-clone"),
    path("program-assignments", ProgramAssignmentView.as_view(), name="program-assignments"),
    path(
        "coach-athlete-assignments",
        CoachAthleteAssignmentView.as_view(),
        name="coach-athlete-assignments",
    ),
]
