"""Seed the deterministic fake provider config and vetted v1 prompt templates.

Contains only non-secret platform-authored content. Idempotent.
"""

from django.db import migrations


def seed(apps, schema_editor):
    from apps.copilot.bootstrap import seed_defaults

    seed_defaults(apps)


def unseed(apps, schema_editor):
    provider = apps.get_model("copilot", "AIProviderAdapterConfig")
    template = apps.get_model("copilot", "PromptTemplateVersion")
    template.objects.filter(version=1).delete()
    provider.objects.filter(slug="fake-deterministic").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("copilot", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, reverse_code=unseed),
    ]
