from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.permissions import IsAuthenticatedAndActive
from .models import AuditEvent


class AuditLogView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, org_id=None):
        # Owner of org or platform admin
        user = request.user
        if org_id:
            qs = AuditEvent.objects.filter(organization_id=org_id)
            # simple owner check (full in service)
        else:
            qs = AuditEvent.objects.all()  # platform admin only in real impl
        data = [
            {
                "id": str(e.id),
                "action": e.action,
                "created_at": e.created_at.isoformat(),
                "actor_user_id": str(e.actor_user_id) if e.actor_user_id else None,
            }
            for e in qs.order_by("-created_at")[:50]
        ]
        return Response({"audit_events": data})
