"""Retention enforcement for Copilot runs (Tier 8 lifecycle).

Usage: ``python manage.py purge_copilot_runs`` — expires runs past their
``expires_at`` timestamp, clearing redacted context snapshots and unapproved
draft payloads. Idempotent; emits one ``ai.purge.executed`` audit event per
expired run.
"""

from django.core.management.base import BaseCommand

from apps.copilot.services import purge_expired_runs


class Command(BaseCommand):
    help = "Expire Copilot runs past their retention window and clear stored context payloads."

    def handle(self, *args, **options):
        count = purge_expired_runs()
        self.stdout.write(f"purged={count}")
