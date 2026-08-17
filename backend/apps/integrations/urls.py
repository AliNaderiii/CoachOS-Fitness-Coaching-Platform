from django.urls import path

from . import views

urlpatterns = [
    path("connect/", views.connect, name="integration-connect"),
    path("callback/", views.callback, name="integration-callback"),
    path("<uuid:connection_id>/sync/", views.sync, name="integration-sync"),
    path("<uuid:connection_id>/status/", views.connection_status, name="integration-status"),
    path("<uuid:connection_id>/disconnect/", views.disconnect, name="integration-disconnect"),
    path("<uuid:connection_id>/provenance/", views.provenance, name="integration-provenance"),
    path("<uuid:connection_id>/events/", views.events, name="integration-events"),
]
