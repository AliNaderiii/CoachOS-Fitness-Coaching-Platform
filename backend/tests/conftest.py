"""Pytest fixtures for CoachOS backend tests."""

import os

import pytest
from rest_framework.test import APIClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")


@pytest.fixture
def api_client():
    return APIClient()
