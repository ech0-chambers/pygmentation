"""Font classification and typography categorization rules for plot styling."""

from enum import StrEnum
from typing import Any


class FontCategory(StrEnum):
    SERIF = "serif"
    SANS_SERIF = "sans-serif"
    UNCLASSIFIED = "unclassified"


# OpenType OS/2 table panose[1] (Serif Style) constants:
# https://learn.microsoft.com/en-us/typography/opentype/spec/os2#panose
_PANOSE_SERIF_STYLES: frozenset[int] = frozenset({2, 3, 4, 5, 6, 7, 8, 9, 10})
_PANOSE_SANS_SERIF_STYLES: frozenset[int] = frozenset({11, 12, 13, 14, 15})

# OpenType OS/2 table sFamilyClass upper byte (Class ID) constants:
# https://learn.microsoft.com/en-us/typography/opentype/spec/os2#sfamilyclass
# Class 1: Oldstyle Serifs, 2: Transitional Serifs, 3: Modern Serifs,
# 4: Clarendon Serifs, 5: Slab Serifs, 7: Freeform Serifs
_IBM_SERIF_CLASSES: frozenset[int] = frozenset({1, 2, 3, 4, 5, 7})
# Class 8: Sans Serif
_IBM_SANS_CLASS: int = 8

# Used when font specification doesn't give a clear indication of serif/sans-serif:
KNOWN_SERIF_KEYWORDS: tuple[str, ...] = (
    "serif",
    "roman",
    "times",
    "georgia",
    "garamond",
    "palatino",
    "cambria",
    "minion",
    "baskerville",
    "caslon",
    "bodoni",
    "didot",
    "bookman",
    "charter",
    "schoolbook",
    "antiqua",
)

KNOWN_SANS_KEYWORDS: tuple[str, ...] = (
    "sans",
    "arial",
    "helvetica",
    "verdana",
    "calibri",
    "tahoma",
    "trebuchet",
    "futura",
    "geneva",
    "optima",
    "corbel",
    "segoe",
    "roboto",
    "cantarell",
    "ubuntu",
    "inter",
    "gothic",
    "fira",
)

# The standard fonts defined in matplotlib's internal font lists:
STANDARD_MATPLOTLIB_SERIF_NAMES: frozenset[str] = frozenset(
    {
        "bitstream vera serif",
        "bookman",
        "century schoolbook l",
        "charter",
        "computer modern roman",
        "dejavu serif",
        "itc bookman",
        "new century schoolbook",
        "nimbus roman no9 l",
        "palatino",
        "times",
        "times new roman",
        "utopia",
    }
)

STANDARD_MATPLOTLIB_SANS_NAMES: frozenset[str] = frozenset(
    {
        "arial",
        "avant garde",
        "bitstream vera sans",
        "computer modern sans serif",
        "dejavu sans",
        "geneva",
        "helvetica",
        "lucid",
        "lucida grande",
        "verdana",
    }
)


def classify_font_name(name: str, *, include_keywords: bool = True) -> FontCategory:
    """Classify a font family name as serif, sans-serif, or unclassified.

    Args:
        name: Font family name (e.g. 'DejaVu Sans', 'Times New Roman').
        include_keywords: If True, check heuristic keywords as a fallback.
            If False, only check standard Matplotlib names and explicit 'sans'/'serif' tokens.

    Returns:
        FontCategory: FontCategory.SERIF, FontCategory.SANS_SERIF, or FontCategory.UNCLASSIFIED.
    """
    lower = name.lower()

    if lower in STANDARD_MATPLOTLIB_SERIF_NAMES:
        return FontCategory.SERIF
    if lower in STANDARD_MATPLOTLIB_SANS_NAMES:
        return FontCategory.SANS_SERIF

    if "sans" in lower:
        return FontCategory.SANS_SERIF
    if "serif" in lower:
        return FontCategory.SERIF

    if include_keywords:
        if any(k in lower for k in KNOWN_SANS_KEYWORDS):
            return FontCategory.SANS_SERIF
        if any(k in lower for k in KNOWN_SERIF_KEYWORDS):
            return FontCategory.SERIF

    return FontCategory.UNCLASSIFIED


def _classify_font_file(
    font_path: str, ft_module: Any
) -> tuple[str, FontCategory] | None:
    # Inspect a font file to determine if it is a serif font, a sans-serif font, or neither/unclear
    if ft_module is None:
        return None

    try:
        font = ft_module.FT2Font(font_path)
    except (RuntimeError, OSError, ValueError):
        return None

    name = font.family_name.strip()
    if not name:
        return None

    # Check explicit name tokens ("sans" / "serif") or recognised fonts
    # Note keywords are excluded, so this hopefully only returns a category if it's definitive
    name_class = classify_font_name(name, include_keywords=False)
    if name_class != FontCategory.UNCLASSIFIED:
        return name, name_class

    # Inspect OS/2 font table Panose and family classification
    try:
        os2 = font.get_sfnt_table("OS/2")
    except (KeyError, RuntimeError, ValueError):
        os2 = None

    if os2:
        pan = os2.get("panose")
        if pan and len(pan) >= 2 and pan[0] == 2:
            if pan[1] in _PANOSE_SANS_SERIF_STYLES:
                return name, FontCategory.SANS_SERIF
            if pan[1] in _PANOSE_SERIF_STYLES:
                return name, FontCategory.SERIF

        s_class = os2.get("sFamilyClass")
        if s_class:
            cls_id = s_class >> 8
            if cls_id in _IBM_SERIF_CLASSES:
                return name, FontCategory.SERIF
            if cls_id == _IBM_SANS_CLASS:
                return name, FontCategory.SANS_SERIF

    # Heuristic keyword fallback
    return name, classify_font_name(name, include_keywords=True)
