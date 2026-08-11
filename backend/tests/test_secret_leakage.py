"""
Tests verifying no private secret values leak in public API responses.
"""

import pytest


@pytest.mark.django_db
def test_meta_and_health_do_not_leak_secrets(api_client):
    forbidden_terms = [
        "secret_key",
        "django-insecure",
        "postgres://",
        "redis://",
        "password",
        "aws_access_key",
    ]

    for path in ["/healthz", "/readyz", "/api/v1/meta"]:
        response = api_client.get(path)
        content = response.content.decode("utf-8")
        for term in forbidden_terms:
            assert term not in content.lower(), f"Potential secret leak '{term}' at {path}"
