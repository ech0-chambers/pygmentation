"""Matplotlib styling and font discovery integration."""

from .fonts import (
    CLASSIC_LATEX_SANS_SERIF_FONTS,
    CLASSIC_LATEX_SERIF_FONTS,
    KNOWN_LATEX_PACKAGES,
    KNOWN_SANS_KEYWORDS,
    KNOWN_SERIF_KEYWORDS,
    LATEX_SANS_SERIF_FONTS,
    LATEX_SERIF_FONTS,
    _classify_font_file,
    _get_latex_fonts,
    _get_non_latex_fonts,
    _get_tex_font_directories,
    _kpsewhich_target_exists,
    _resolve_font_types,
    _resolve_latex_package_from_path,
    get_fonts,
    is_latex_available,
)
from .style import (
    DocType,
    apply_plot_styles,
    init,
    init_matplotlib,
)

__all__ = [
    "DocType",
    "apply_plot_styles",
    "init",
    "init_matplotlib",
    "get_fonts",
    "is_latex_available",
    "CLASSIC_LATEX_SERIF_FONTS",
    "CLASSIC_LATEX_SANS_SERIF_FONTS",
    "LATEX_SERIF_FONTS",
    "LATEX_SANS_SERIF_FONTS",
    "KNOWN_LATEX_PACKAGES",
    "KNOWN_SERIF_KEYWORDS",
    "KNOWN_SANS_KEYWORDS",
    "_classify_font_file",
    "_get_latex_fonts",
    "_get_non_latex_fonts",
    "_get_tex_font_directories",
    "_kpsewhich_target_exists",
    "_resolve_font_types",
    "_resolve_latex_package_from_path",
]
