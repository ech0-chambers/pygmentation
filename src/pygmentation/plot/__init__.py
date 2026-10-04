"""Matplotlib styling and font discovery integration."""

from .font_category import (
    FontCategory,
    _classify_font_file,
    classify_font_name,
)
from .fonts import (
    KNOWN_LATEX_PACKAGES,
    _clean_tex_directory,
    _get_latex_fonts,
    _get_non_latex_fonts,
    _get_tex_font_directories,
    _get_texmf_roots,
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
    "FontCategory",
    "apply_plot_styles",
    "init",
    "init_matplotlib",
    "get_fonts",
    "is_latex_available",
    "classify_font_name",
    "KNOWN_LATEX_PACKAGES",
    "_classify_font_file",
    "_clean_tex_directory",
    "_get_latex_fonts",
    "_get_non_latex_fonts",
    "_get_tex_font_directories",
    "_get_texmf_roots",
    "_kpsewhich_target_exists",
    "_resolve_font_types",
    "_resolve_latex_package_from_path",
]
