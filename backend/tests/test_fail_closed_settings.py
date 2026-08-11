"""
Tests verifying fail-closed configuration in staging and production settings (ADR-048 Correction).
"""

import importlib

import pytest
from django.core.exceptions import ImproperlyConfigured


def test_staging_fails_without_secret_key(monkeypatch):
    monkeypatch.delenv("DJANGO_SECRET_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "staging.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://staging.coachos.io")

    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        import config.settings.staging as staging_settings

        importlib.reload(staging_settings)


def test_staging_fails_with_insecure_secret_key(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "django-insecure-test")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "staging.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://staging.coachos.io")

    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        import config.settings.staging as staging_settings

        importlib.reload(staging_settings)


def test_production_fails_without_database_url(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")

    with pytest.raises(ImproperlyConfigured, match="DATABASE_URL"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_production_fails_with_wildcard_allowed_hosts(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "*")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")

    with pytest.raises(ImproperlyConfigured, match="ALLOWED_HOSTS"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_production_fails_without_cors_origins(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io")
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    with pytest.raises(ImproperlyConfigured, match="CORS_ALLOWED_ORIGINS"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)
