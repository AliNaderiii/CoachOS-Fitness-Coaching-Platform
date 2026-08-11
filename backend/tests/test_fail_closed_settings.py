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
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://staging.coachos.io")
    monkeypatch.setenv("REDIS_URL", "redis://redis.staging:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.staging:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.staging:6379/2")

    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        import config.settings.staging as staging_settings

        importlib.reload(staging_settings)


def test_staging_fails_with_insecure_secret_key(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "django-insecure-test")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "staging.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://staging.coachos.io")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://staging.coachos.io")
    monkeypatch.setenv("REDIS_URL", "redis://redis.staging:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.staging:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.staging:6379/2")

    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        import config.settings.staging as staging_settings

        importlib.reload(staging_settings)


def test_production_fails_without_database_url(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.prod:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.prod:6379/2")

    with pytest.raises(ImproperlyConfigured, match="DATABASE_URL"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_production_fails_with_wildcard_allowed_hosts(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "*")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.prod:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.prod:6379/2")

    with pytest.raises(ImproperlyConfigured, match="ALLOWED_HOSTS"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_production_fails_without_cors_origins(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io")
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.prod:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.prod:6379/2")

    with pytest.raises(ImproperlyConfigured, match="CORS_ALLOWED_ORIGINS"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_production_fails_without_csrf_trusted_origins(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")
    monkeypatch.delenv("CSRF_TRUSTED_ORIGINS", raising=False)
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.prod:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.prod:6379/2")

    with pytest.raises(ImproperlyConfigured, match="CSRF_TRUSTED_ORIGINS"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_production_fails_without_redis_url(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://app.coachos.io")
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.prod:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.prod:6379/2")

    with pytest.raises(ImproperlyConfigured, match="REDIS_URL"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_production_fails_without_celery_broker_url(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/0")
    monkeypatch.delenv("CELERY_BROKER_URL", raising=False)
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.prod:6379/2")

    with pytest.raises(ImproperlyConfigured, match="CELERY_BROKER_URL"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_production_fails_without_celery_result_backend(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.prod:6379/1")
    monkeypatch.delenv("CELERY_RESULT_BACKEND", raising=False)

    with pytest.raises(ImproperlyConfigured, match="CELERY_RESULT_BACKEND"):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)


def test_valid_production_configuration_succeeds(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "complex-production-secret-key-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@db:5432/db")
    monkeypatch.setenv("ALLOWED_HOSTS", "app.coachos.io,api.coachos.io")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://app.coachos.io")
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.prod:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.prod:6379/2")

    import config.settings.production as prod_settings

    importlib.reload(prod_settings)

    assert prod_settings.DEBUG is False
    assert "app.coachos.io" in prod_settings.ALLOWED_HOSTS
    assert "https://app.coachos.io" in prod_settings.CORS_ALLOWED_ORIGINS
    assert "https://app.coachos.io" in prod_settings.CSRF_TRUSTED_ORIGINS
    assert prod_settings.REDIS_URL == "redis://redis.prod:6379/0"
    assert prod_settings.CELERY_BROKER_URL == "redis://redis.prod:6379/1"
    assert prod_settings.CELERY_RESULT_BACKEND == "redis://redis.prod:6379/2"
