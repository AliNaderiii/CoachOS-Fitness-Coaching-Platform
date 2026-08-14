from django.urls import path

from .views import (
    AcceptInvitationView,
    InvitationListCreateView,
    LocationView,
    MemberListView,
    MembershipUpdateView,
    OrganizationDetailView,
    OrganizationListCreateView,
)

urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="org-list-create"),
    path("<str:org_id>", OrganizationDetailView.as_view(), name="org-detail"),
    path("<str:org_id>/locations", LocationView.as_view(), name="org-location"),
    path("<str:org_id>/invitations", InvitationListCreateView.as_view(), name="org-invitations"),
    path(
        "invitations/<str:token>/accept", AcceptInvitationView.as_view(), name="invitation-accept"
    ),
    path("<str:org_id>/members", MemberListView.as_view(), name="org-members"),
    path(
        "<str:org_id>/members/<str:membership_id>",
        MembershipUpdateView.as_view(),
        name="org-member-update",
    ),
]
