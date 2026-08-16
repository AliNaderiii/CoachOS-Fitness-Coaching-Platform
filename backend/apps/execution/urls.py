from django.urls import path

from .views import (
    AthleteTodayView,
    BodyMetricView,
    ConsentView,
    FeedbackFlagView,
    ProgressPhotoView,
    SetLogView,
    SubstitutionView,
    WorkoutSessionDetailView,
    WorkoutSessionListCreateView,
)

urlpatterns = [
    path("athlete/today", AthleteTodayView.as_view(), name="athlete-today"),
    path("workout-sessions", WorkoutSessionListCreateView.as_view(), name="workout-sessions"),
    path(
        "workout-sessions/<str:session_id>",
        WorkoutSessionDetailView.as_view(),
        name="workout-session-detail",
    ),
    path(
        "workout-sessions/<str:session_id>/set-logs",
        SetLogView.as_view(),
        name="workout-session-set-logs",
    ),
    path(
        "workout-sessions/<str:session_id>/substitutions",
        SubstitutionView.as_view(),
        name="workout-session-substitutions",
    ),
    path(
        "workout-sessions/<str:session_id>/feedback-flags",
        FeedbackFlagView.as_view(),
        name="workout-session-feedback-flags",
    ),
    path(
        "athletes/<str:athlete_id>/progress/photos",
        ProgressPhotoView.as_view(),
        name="progress-photos",
    ),
    path(
        "athletes/<str:athlete_id>/body-metrics",
        BodyMetricView.as_view(),
        name="body-metrics",
    ),
    path("consents", ConsentView.as_view(), name="consents"),
]
