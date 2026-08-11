"""
Tests verifying secure default permissions in Django REST Framework (ADR-048 Correction).
"""

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ProtectedView(APIView):
    """View inheriting default REST_FRAMEWORK permission classes (IsAuthenticated)."""

    def get(self, request):
        return Response({"secret_data": "athlete-records"})


def test_default_permission_is_authenticated():
    default_perms = settings.REST_FRAMEWORK.get("DEFAULT_PERMISSION_CLASSES", [])
    assert "rest_framework.permissions.IsAuthenticated" in default_perms


def test_unauthenticated_request_to_protected_view_is_denied():
    from django.test import RequestFactory

    factory = RequestFactory()
    request = factory.get("/api/v1/protected")

    view = ProtectedView.as_view()
    response = view(request)

    # DRF will raise AuthenticationFailed or NotAuthenticated -> 401 Unauthorized or 403 Forbidden
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_public_health_endpoints_remain_accessible(api_client):
    assert api_client.get("/healthz").status_code == status.HTTP_200_OK
    assert api_client.get("/readyz").status_code in (
        status.HTTP_200_OK,
        status.HTTP_503_SERVICE_UNAVAILABLE,
    )
    assert api_client.get("/api/v1/meta").status_code == status.HTTP_200_OK
