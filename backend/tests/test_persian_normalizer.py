"""Tests for Persian Text Normalizer."""

from apps.core.utils.persian_normalizer import PersianNormalizer


def test_arabic_yeh_and_kaf_folding():
    # Arabic Yeh (ي U+064A) and Arabic Kaf (ك U+0643)
    raw = "حركت اسكوات با هالتر يكي"
    normalized = PersianNormalizer.normalize(raw)

    assert "ک" in normalized  # Keheh
    assert "ی" in normalized  # Persian Yeh
    assert "ك" not in normalized
    assert "ي" not in normalized


def test_arabic_indic_digit_folding():
    # Arabic digits ٠١٢٣٤٥٦٧٨٩
    raw = "پرس سینه ۳ ست ۱۰ تکرار ١٢٣٤٥"
    normalized = PersianNormalizer.normalize(raw)

    assert "۱۲۳۴۵" in normalized or "12345" in normalized
    assert "١" not in normalized
    assert "٤" not in normalized


def test_diacritics_stripping():
    # Fatha, Damma, Kasra, Tashdid
    raw = "حَرَکَتِ اِسْکُوات"
    normalized = PersianNormalizer.normalize(raw)

    assert normalized == "حرکت اسکوات"


def test_zwnj_normalization():
    # Zero-Width Non-Joiner
    raw = "می‌خواهم شنا\u200cسوئدی"
    normalized = PersianNormalizer.normalize(raw, preserve_zwnj=False)

    assert "\u200c" not in normalized
    assert "شنا" in normalized
    assert "می خواهم" in normalized
