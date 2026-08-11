"""
ASGI config for CoachOS.
Requires explicit DJANGO_SETTINGS_MODULE in production/staging.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_asgi_application()
