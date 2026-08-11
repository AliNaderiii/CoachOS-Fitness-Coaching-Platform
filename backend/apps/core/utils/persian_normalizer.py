"""
Persian Search Normalization Utility.
Phase 04 Foundation - Implements Perso-Arabic script keyboard-variant folding (ADR-018).
Note: This utility handles keyboard character folding for Persian search queries.
Arabic is strictly out of scope as a product language (ADR-003).
"""

import re
import unicodedata

# Character replacement mappings
CHAR_MAP = {
    "\u064a": "\u06cc",  # Arabic Yeh (ي) -> Persian Yeh (ی)
    "\u0649": "\u06cc",  # Arabic Alef Maksura (ى) -> Persian Yeh (ی)
    "\u0643": "\u06a9",  # Arabic Kaf (ك) -> Persian Keheh (ک)
    "\u0629": "\u0647",  # Arabic Ta Marbuta (ة) -> Persian Heh (ه)
    "\u06c0": "\u0647",  # Persian Heh with Yeh above (ۀ) -> Heh (ه)
    "\u0624": "\u0648",  # Waw with Hamza (ؤ) -> Waw (و)
    "\u0626": "\u06cc",  # Yeh with Hamza (ئ) -> Yeh (ی)
    "\u0622": "\u0627",  # Alef with Madda (آ) -> Alef (ا)
    "\u0623": "\u0627",  # Alef with Hamza above (أ) -> Alef (ا)
    "\u0625": "\u0627",  # Alef with Hamza below (إ) -> Alef (ا)
}

# Arabic-Indic digits to Persian digits
ARABIC_DIGITS_MAP = {
    "\u0660": "\u06f0",  # ٠ -> ۰
    "\u0661": "\u06f1",  # ١ -> ۱
    "\u0662": "\u06f2",  # ٢ -> ۲
    "\u0663": "\u06f3",  # ٣ -> ۳
    "\u0664": "\u06f4",  # ٤ -> ۴
    "\u0665": "\u06f5",  # ٥ -> ۵
    "\u0666": "\u06f6",  # ٦ -> ۶
    "\u0667": "\u06f7",  # ٧ -> ۷
    "\u0668": "\u06f8",  # ٨ -> ۸
    "\u0669": "\u06f9",  # ٩ -> ۹
}

# Diacritics regex (Fatha, Damma, Kasra, Tanwin, Tashdid, Sukun, Harakat)
DIACRITICS_REGEX = re.compile(r"[\u064B-\u0652\u0656-\u065F\u0670\u06D6-\u06ED]")

# Zero-Width Non-Joiner (ZWNJ) and Zero-Width Joiner (ZWJ)
ZWNJ = "\u200c"
ZWJ = "\u200d"


class PersianNormalizer:
    """Normalizes Persian text queries and alias records for pg_trgm indexing."""

    @classmethod
    def normalize(cls, text: str, preserve_zwnj: bool = False) -> str:
        """
        Full Persian text normalization pipeline:
        1. Unicode NFKC normalization
        2. Character folding (Arabic Yeh/Kaf -> Persian Yeh/Keheh)
        3. Digit normalization
        4. Diacritics stripping
        5. ZWNJ normalization (space or preserved)
        6. Whitespace cleanup
        """
        if not text or not isinstance(text, str):
            return ""

        # Step 1: Unicode NFKC
        text = unicodedata.normalize("NFKC", text)

        # Step 2: Character folding
        for src, target in CHAR_MAP.items():
            text = text.replace(src, target)

        # Step 3: Digit normalization
        for src, target in ARABIC_DIGITS_MAP.items():
            text = text.replace(src, target)

        # Step 4: Remove diacritics
        text = DIACRITICS_REGEX.sub("", text)

        # Step 5: Handle ZWNJ / ZWJ
        if not preserve_zwnj:
            text = text.replace(ZWNJ, " ").replace(ZWJ, "")
        else:
            text = text.replace(ZWJ, "")

        # Step 6: Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text.lower()
