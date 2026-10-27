"""Matplotlib styling and font discovery integration."""

from .font_category import (
    FontCategory,
    classify_font_name,
)
from .fonts import (
    KNOWN_LATEX_PACKAGES,
    get_fonts,
    is_latex_available,
)
from .style import (
    DocType,
    apply_plot_styles,
)

__all__ = [
    "DocType",
    "FontCategory",
    "apply_plot_styles",
    "get_fonts",
    "is_latex_available",
    "classify_font_name",
    "KNOWN_LATEX_PACKAGES",
]

