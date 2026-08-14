from django.urls import path

from .views import ExerciseDetailView, ExerciseListCreateView, ExerciseModerationView

urlpatterns = [
    path("exercises", ExerciseListCreateView.as_view(), name="exercise-list-create"),
    path("exercises/<str:exercise_id>", ExerciseDetailView.as_view(), name="exercise-detail"),
    path(
        "admin/exercises/moderation",
        ExerciseModerationView.as_view(),
        name="exercise-moderation",
    ),
]
