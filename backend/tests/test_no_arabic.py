"""
Tests ensuring Arabic resources are strictly absent (ADR-003).
"""

from pathlib import Path

from django.conf import settings


def test_no_arabic_locale_in_django_settings():
    lang_codes = [code for code, _ in settings.LANGUAGES]
    assert "ar" not in lang_codes
    assert "ar-SA" not in lang_codes
    assert "fa" in lang_codes or "fa-ir" in str(lang_codes).lower()
    assert "en" in lang_codes or "en-us" in str(lang_codes).lower()


def test_no_arabic_translation_files_in_repository():
    repo_root = Path(__file__).resolve().parent.parent.parent
    # Scan for any ar.json or ar-*.json locale files
    arabic_json_files = list(repo_root.glob("**/ar*.json"))
    arabic_po_files = list(repo_root.glob("**/ar*.po"))

    # Exclude node_modules and .venv if present
    filtered_json = [
        f for f in arabic_json_files if "node_modules" not in str(f) and ".venv" not in str(f)
    ]
    filtered_po = [
        f for f in arabic_po_files if "node_modules" not in str(f) and ".venv" not in str(f)
    ]

    assert len(filtered_json) == 0, f"Found forbidden Arabic json files: {filtered_json}"
    assert len(filtered_po) == 0, f"Found forbidden Arabic po files: {filtered_po}"
