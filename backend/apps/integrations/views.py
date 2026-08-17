from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .adapters.mock_adapter import MockFitnessProviderAdapter
from .serializers import IntegrationConnectionSerializer

adapter = MockFitnessProviderAdapter()


@api_view(["POST"])
@permission_classes([])
def connect(request):
    return Response({"authorization_url": "/mock/oauth/authorize?provider=mock_fitness&scope=read_activity"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([])
def callback(request):
    return Response({"connection_state": "connected", "message": "Mock authorization completed."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([])
def sync(request, connection_id):
    events = adapter.generate_events()
    adapter.simulate_rate_limit(1)
    return Response({"events_imported": len(events), "cursor_updated": True}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([])
def status(request, connection_id):
    return Response({
        "connection_state": "connected",
        "last_sync_at": adapter.EVENT_TEMPLATE.get("provider_timestamp"),
        "provider_rate_limit_remaining": adapter.rate_limit_remaining,
        "provider_rate_limit_reset": adapter.rate_limit_reset,
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([])
def provenance(request, connection_id):
    return Response({"provider_timestamp": "2026-08-09T00:00:00Z", "provider_event_id": "mock_event_001", "imported_at": "2026-08-16T10:30:00Z"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([])
def events(request, connection_id):
    return Response(adapter.generate_events(), status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([])
def disconnect(request, connection_id):
    return Response({"connection_state": "disconnected", "revocation_status": "pending"}, status=status.HTTP_200_OK)
