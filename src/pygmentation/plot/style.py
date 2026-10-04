"""Matplotlib rcParams styling and color scheme configuration."""

from enum import IntEnum
from typing import Any

from pygmentation.colors.scheme import ColorScheme, SchemeType
from pygmentation.registry import registry

from . import fonts


class DocType(IntEnum):

    REPORT = 1
    PRESENTATION = 2


def apply_plot_styles(
    scheme: str | ColorScheme = "nord",
    scheme_type: str | SchemeType = SchemeType.LIGHT,
    doc_type: str | DocType = DocType.REPORT,
    transparent: bool = False,
    use_latex: bool | None = None,
    font_family: str = "serif",
    font_serif: str | None = None,
    font_sans_serif: str | None = None,
    font: str | None = None,
) -> dict[str, Any]:
    """Configure matplotlib rcParams to use a pygmentation color scheme and some sensible presets.

    Args:
        scheme: Scheme name to resolve from registry, or an initialized ColorScheme instance.
        scheme_type: Scheme variant ('light' (default) or 'dark', or SchemeType enum). Ignored if scheme is a ColorScheme object.
        doc_type: Document style target ('report' (default) or 'presentation', or DocType enum). Affects things like aspect ratio, default font size, and axis visibility.
        transparent: If True, set figure and axes background to transparent ('none').
        use_latex: If True, enable LaTeX rendering (text.usetex). If None, checks for available LaTeX compiler. Defaults to None.
        font_family: Matplotlib font family ('serif', 'sans-serif', etc.). Defaults to 'serif'.
        font_serif: Font name for serif family (font.serif). Defaults to 'Computer Modern Roman' if unspecified.
        font_sans_serif: Font name for sans-serif family (font.sans-serif).
        font: General font name. If specified and font_serif/font_sans_serif are omitted, used for both.

    Returns:
        dict: The updated rcParams dictionary applied to matplotlib.

    Raises:
        ImportError: If 'cycler' or 'matplotlib' is not installed.
        SchemeNotFoundError: If a scheme name string cannot be resolved by the registry.
        ValueError: If scheme_type or doc_type strings are unrecognized.
    """
    try:
        from cycler import cycler
    except ImportError:
        raise ImportError(
            "The 'cycler' package is required for plot functionality. "
            "Please install it using 'pip install cycler' or 'pip install pygmentation[plots]'."
        )
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError(
            "The 'matplotlib' package is required for plot functionality. "
            "Please install it using 'pip install matplotlib' or 'pip install pygmentation[plots]'."
        )

    # Normalize doc_type
    if isinstance(doc_type, str):
        try:
            doc_type = DocType[doc_type.upper()]
        except KeyError:
            valid_docs = [d.name.lower() for d in DocType]
            raise ValueError(
                f"Invalid doc_type '{doc_type}'. Expected one of: {valid_docs}"
            )

    # Resolve scheme
    if isinstance(scheme, str):
        if isinstance(scheme_type, str):
            try:
                scheme_type = SchemeType[scheme_type.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid scheme_type '{scheme_type}'. Expected 'light' or 'dark'."
                )
        scheme_obj = registry.get(scheme, variant=scheme_type)
    elif isinstance(scheme, ColorScheme):
        scheme_obj = scheme
    else:
        raise TypeError(
            f"Expected scheme name (str) or ColorScheme instance, got {type(scheme).__name__}"
        )

    distinct = scheme_obj.distinct if scheme_obj.distinct else [scheme_obj.foreground]

    color_cycler = cycler(
        color=[c.base.css for c in distinct]
        + [c.base.css for c in distinct]
        + [c.base.css for c in distinct],
        linestyle=["-"] * len(distinct)
        + ["--"] * len(distinct)
        + [":"] * len(distinct),
    )

    legend_face = (
        scheme_obj.background[5].css
        if len(scheme_obj.background.variants) >= 5
        else scheme_obj.background.base.css
    )

    axes_color = (
        scheme_obj.foreground.css
        if doc_type == DocType.REPORT
        else distinct[0].css
    )

    if font is not None:
        if font_serif is None:
            font_serif = font
        if font_sans_serif is None:
            font_sans_serif = font

    if font_serif is None:
        font_serif = "Computer Modern Roman"

    if use_latex is None:
        use_latex = fonts.is_latex_available()

    new_params: dict[str, Any] = {
        "text.usetex": use_latex,
        "font.family": font_family,
        "font.serif": font_serif,
        "text.color": scheme_obj.foreground.css,
        "font.size": 12 if doc_type == DocType.REPORT else 16,
        "figure.facecolor": (
            scheme_obj.background.base.css
            if not transparent
            else "none"
        ),
        "axes.facecolor": scheme_obj.background.base.css if not transparent else "none",
        "legend.facecolor": legend_face,
        "legend.edgecolor": scheme_obj.foreground.css,
        "legend.framealpha": 0.5,
        "legend.fancybox": True,
        "axes.prop_cycle": color_cycler,
        "axes.edgecolor": axes_color,
        "axes.labelcolor": axes_color,
        "axes.spines.top": True if doc_type == DocType.REPORT else False,
        "axes.spines.right": True if doc_type == DocType.REPORT else False,
        "xtick.color": axes_color,
        "ytick.color": axes_color,
        "figure.figsize": (6.4, 4.8) if doc_type == DocType.REPORT else (8, 4.5),
        "figure.dpi": 300,
    }

    if font_sans_serif is not None:
        new_params["font.sans-serif"] = font_sans_serif

    if use_latex:
        preamble_lines = [r"\usepackage{amsmath, amssymb}"]
        latex_serif, latex_sans = fonts._get_latex_fonts()
        active_font = font_sans_serif if font_family == "sans-serif" else font_serif
        packages_to_load: list[str] = []
        for f_name in (active_font, font_serif, font_sans_serif):
            if f_name:
                pkg = latex_serif.get(f_name) or latex_sans.get(f_name)
                if pkg is not None and pkg not in packages_to_load:
                    packages_to_load.append(pkg)
        for pkg in packages_to_load:
            preamble_lines.append(rf"\usepackage{{{pkg}}}")
        new_params["text.latex.preamble"] = "\n".join(preamble_lines)

    plt.rcParams.update(new_params)
    return new_params


