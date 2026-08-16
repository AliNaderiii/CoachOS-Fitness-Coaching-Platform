"""Phase 08 additive routes under /api/v1."""

from django.urls import path

from .views import (
    ConversationDetailView,
    ConversationListCreateView,
    ConversationMuteView,
    ConversationReadView,
    MessageListCreateView,
    NotificationListView,
    NotificationPreferenceView,
    NotificationReadAllView,
    NotificationReadView,
)

urlpatterns = [
    path("conversations", ConversationListCreateView.as_view(), name="conversations"),
    path(
        "conversations/<str:conversation_id>",
        ConversationDetailView.as_view(),
        name="conversation-detail",
    ),
    path(
        "conversations/<str:conversation_id>/messages",
        MessageListCreateView.as_view(),
        name="conversation-messages",
    ),
    path(
        "conversations/<str:conversation_id>/read",
        ConversationReadView.as_view(),
        name="conversation-read",
    ),
    path(
        "conversations/<str:conversation_id>/mute",
        ConversationMuteView.as_view(),
        name="conversation-mute",
    ),
    path("notifications", NotificationListView.as_view(), name="notifications"),
    path(
        "notifications/read-all",
        NotificationReadAllView.as_view(),
        name="notifications-read-all",
    ),
    path(
        "notifications/<str:notification_id>/read",
        NotificationReadView.as_view(),
        name="notification-read",
    ),
    path(
        "notification-preferences",
        NotificationPreferenceView.as_view(),
        name="notification-preferences",
    ),
]
