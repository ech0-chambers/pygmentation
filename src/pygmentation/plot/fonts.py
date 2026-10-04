"""Font discovery and TeX package resolution for plot styling."""

import os
import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

from .font_category import FontCategory, _classify_font_file, classify_font_name


def is_latex_available() -> bool:
    """Check whether a LaTeX compiler is available in the system PATH."""
    return bool(shutil.which("latex") or shutil.which("pdflatex"))


# LaTeX fonts for which matplotlib will automatically insert the required packages into the
# preamble
CLASSIC_LATEX_SERIF_TARGETS: dict[str, str] = {
    "Bookman": "pbkr8t.tfm",
    "Charter": "charter.sty",
    "Computer Modern Roman": "cmr10.tfm",
    "New Century Schoolbook": "pncr8t.tfm",
    "Palatino": "mathpazo.sty",
    "Times": "mathptmx.sty",
}

CLASSIC_LATEX_SANS_SERIF_TARGETS: dict[str, str] = {
    "Avant Garde": "avant.sty",
    "Computer Modern Sans Serif": "cmss10.tfm",
    "Helvetica": "helvet.sty",
}

ALL_CLASSIC_LATEX_FONTS: frozenset[str] = frozenset(
    CLASSIC_LATEX_SERIF_TARGETS
) | frozenset(CLASSIC_LATEX_SANS_SERIF_TARGETS)


# Quick look-up for common fonts and their packages
KNOWN_LATEX_PACKAGES: dict[str, str] = {
    # Sans-serif
    "Cabin": "cabin",
    "Cantarell": "cantarell",
    "Carlito": "carlito",
    "Comfortaa": "comfortaa",
    "DejaVu Sans": "DejaVuSans",
    "Fira Mono": "FiraMono",
    "Fira Sans": "FiraSans",
    "Fira Sans Light": "FiraSans",
    "Inconsolata": "inconsolata",
    "Inter": "inter",
    "Iwona": "iwona",
    "Kurier": "kurier",
    "Lato": "lato",
    "Linux Biolinum O": "biolinum",
    "Open Sans": "opensans",
    "Overpass": "overpass",
    "Raleway": "raleway",
    "Roboto": "roboto",
    "Source Code Pro": "sourcecodepro",
    "Source Sans 3": "sourcesans3",
    "Source Sans Pro": "sourcesanspro",
    # Serif
    "Cinzel": "cinzel",
    "Coelacanth": "coelacanth",
    "EBGaramond": "ebgaramond",
    "Heuristica": "heuristica",
    "Latin Modern Mono": "lmodern",
    "Latin Modern Roman": "lmodern",
    "Latin Modern Sans": "lmodern",
    "Linux Libertine O": "libertine",
    "Playfair Display": "playfair",
    "Source Serif 4": "sourceserif4",
    "Source Serif Pro": "sourceserifpro",
    "XCharter": "XCharter",
}


def _kpsewhich_target_exists(target: str) -> bool:
    # Check if kpsewhich can find a target font
    try:
        res = subprocess.run(
            ["kpsewhich", target],
            capture_output=True,
            text=True,
            timeout=2,
        )
        return bool(res.stdout.strip())
    except (subprocess.SubprocessError, OSError):
        return False


def _clean_tex_directory(raw_path: str) -> Path | None:

    clean = raw_path.strip().lstrip("!").rstrip("/\\")
    while clean.endswith(("//", "\\\\")):
        clean = clean[:-2]

    if not clean or clean == "." or "tex" not in clean.lower():
        return None

    try:
        p = Path(clean).expanduser().resolve()
        return p if p.is_dir() else None
    except (OSError, RuntimeError):
        return None


@lru_cache(maxsize=1)
def _get_texmf_roots() -> list[str]:
    # Find all active TeX root (texmf) directory paths using kpsewhich.
    if not shutil.which("kpsewhich"):
        return []

    roots: set[Path] = set()

    # 1. Query composite TEXMF variable (all active distribution and local trees)
    try:
        res = subprocess.run(
            ["kpsewhich", "-var-value=TEXMF"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        raw_val = res.stdout.strip()
        if raw_val:
            if raw_val.startswith("{") and raw_val.endswith("}"):
                raw_val = raw_val[1:-1]
            for segment in re.split(r"[,;]", raw_val):
                clean = segment.strip().lstrip("!").strip("{}").rstrip("/\\")
                if clean:
                    try:
                        p = Path(clean).expanduser().resolve()
                        if p.is_dir():
                            roots.add(p)
                    except (OSError, RuntimeError):
                        pass
    except (subprocess.SubprocessError, OSError):
        pass

    # 2. Query explicit standard variables as fallback/supplement
    for var in (
        "TEXMFDIST",
        "TEXMFLOCAL",
        "TEXMFHOME",
        "TEXMFSYSVAR",
        "TEXMFSYSCONFIG",
    ):
        try:
            res = subprocess.run(
                ["kpsewhich", f"-var-value={var}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            clean = res.stdout.strip().lstrip("!").rstrip("/\\")
            if clean:
                try:
                    p = Path(clean).expanduser().resolve()
                    if p.is_dir():
                        roots.add(p)
                except (OSError, RuntimeError):
                    pass
        except (subprocess.SubprocessError, OSError):
            continue

    # Return roots sorted longest-first so deeper paths match before their parents
    return [str(p) for p in sorted(roots, key=lambda p: len(p.parts), reverse=True)]


@lru_cache(maxsize=1)
def _get_tex_font_directories() -> list[str]:
    # Find directories containing TeX OpenType and TrueType fonts using kpsewhich.
    if not shutil.which("kpsewhich"):
        return []

    roots = _get_texmf_roots()
    dirs: set[str] = set()

    # 1. Search standard TDS font directories under each known root
    for r in roots:
        base = Path(r)
        for sub in ("opentype", "truetype"):
            subpath = base / "fonts" / sub
            if subpath.is_dir():
                dirs.add(str(subpath))

    # 2. Query kpsewhich for format search paths
    for fmt in ("opentype fonts", "truetype fonts"):
        try:
            res = subprocess.run(
                ["kpsewhich", f"-show-path={fmt}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (subprocess.SubprocessError, OSError):
            continue

        for raw in res.stdout.strip().split(os.pathsep):
            cleaned = _clean_tex_directory(raw)
            if cleaned is not None:
                dirs.add(str(cleaned))

    return sorted(dirs)


def _resolve_latex_package_from_path(
    font_path: str,
    family_name: str,
    texmf_roots: list[str] | tuple[str, ...] | None = None,
) -> str | None:
    # Find the LaTeX package (.sty) corresponding to a font file via TDS layout.

    p = Path(font_path).resolve()

    # 1. Prefix match against known texmf roots
    roots = texmf_roots if texmf_roots is not None else _get_texmf_roots()
    texmf_root: Path | None = None

    for r in roots:
        root_path = Path(r).resolve()
        if p.is_relative_to(root_path):
            texmf_root = root_path
            break

    # 2. Structural fallback: identify texmf_root from closest 'fonts' ancestor
    # (supports mock TDS trees in tests and custom trees outside default search roots)
    if texmf_root is None:
        for parent in p.parents:
            if parent.name.lower() == "fonts":
                texmf_root = parent.parent
                break

    if texmf_root is None:
        # No texmf root directory. We probably shouldn't be able to get here unless the user does
        # something strange or the texmf tree is mutated somehow
        return None

    pkg_dir_name = p.parent.name
    latex_dir = texmf_root / "tex" / "latex" / pkg_dir_name
    if not latex_dir.is_dir():
        # We might be on a case-insensitive system where the package name has a different
        # capitalisation
        latex_dir = texmf_root / "tex" / "latex" / pkg_dir_name.lower()

    if not latex_dir.is_dir():
        # Still can't find the directory, not much left to try
        return None

    try:
        sty_files = list(latex_dir.glob("*.sty"))
    except OSError:
        return None

    if not sty_files:
        return None

    # Font file is likely to be the same as the font family name, but with any non-alphanumeric
    # characters (mostly spaces) stripped out
    clean_name = "".join(c for c in family_name if c.isalnum()).lower()
    pkg_lower = pkg_dir_name.lower()

    # 1. Exact match with family name (case-insensitive, e.g. FiraSans.sty for 'Fira Sans')
    for s in sty_files:
        if s.stem.lower() == clean_name:
            return s.stem

    # 2. Exact match with package directory name (e.g. kurier.sty for 'kurier')
    for s in sty_files:
        if s.stem.lower() == pkg_lower:
            return s.stem

    # 3. Exactly one .sty file in the package directory
    if len(sty_files) == 1:
        return sty_files[0].stem

    # 4. Stem matches a prefix or substring in clean font name
    for s in sty_files:
        if s.stem.lower() in clean_name:
            return s.stem

    return None


@lru_cache(maxsize=1)
def _get_latex_fonts() -> tuple[dict[str, str | None], dict[str, str | None]]:
    # Dynamically scan available LaTeX fonts on the system and map them to their packages.

    if not is_latex_available():
        return {}, {}

    import matplotlib.font_manager as fm

    ft: Any = None
    try:
        # We'll use matplotlib's font inspection module to inspect font tables if it's available
        import matplotlib.ft2font as ft
    except ImportError:
        pass

    serif_fonts: dict[str, str | None] = {}
    sans_serif_fonts: dict[str, str | None] = {}

    def record_font(name: str, category: FontCategory, pkg: str | None = None) -> bool:
        if category == FontCategory.SERIF:
            dest = serif_fonts
        elif category == FontCategory.SANS_SERIF:
            dest = sans_serif_fonts
        else:
            return False

        # Add the font if we haven't already. Alternatively, if we have already added it
        # but couldn't find a package last time, and we now have a package, update the package.
        if name not in dest or (dest[name] is None and pkg is not None):
            dest[name] = pkg
        return True

    # 1. Discover classic built-in LaTeX fonts
    # Check if kpsewhich is available for probing LaTeX fonts
    has_kpsewhich = bool(shutil.which("kpsewhich"))

    for targets, category in (
        (CLASSIC_LATEX_SERIF_TARGETS, FontCategory.SERIF),
        (CLASSIC_LATEX_SANS_SERIF_TARGETS, FontCategory.SANS_SERIF),
    ):
        for name, target in targets.items():
            # These are the standard fonts that Matplotlib will handle without us specifying the
            # package, so we can add them to the dictionary without a package. If kpsewhich is
            # available, we'll check that it can resolve the font; if not, then we'll assume it can
            # for now.
            if not has_kpsewhich or _kpsewhich_target_exists(target):
                record_font(name, category, None)

    # 2. Discover and classify modern OpenType/TrueType fonts in TeX trees
    tex_dirs = _get_tex_font_directories()
    if tex_dirs:
        try:
            # findSystemFonts internally deduplicates, so font_files contains unique paths
            font_files = fm.findSystemFonts(fontpaths=tex_dirs)
        except (OSError, RuntimeError):
            font_files = []

        for f in font_files:
            classification = _classify_font_file(f, ft)
            if classification is None:
                continue

            name, category = classification
            # If it's in the list of classic LaTeX fonts, it's already been added above, so skip it
            if name in ALL_CLASSIC_LATEX_FONTS:
                continue

            # 3. Resolve corresponding LaTeX package (.sty)
            pkg = KNOWN_LATEX_PACKAGES.get(name) or _resolve_latex_package_from_path(
                f, name
            )
            record_font(name, category, pkg)

    return serif_fonts, sans_serif_fonts


@lru_cache(maxsize=1)
def _get_non_latex_fonts() -> tuple[set[str], set[str]]:
    # Scan available system fonts via matplotlib and categorize into (serif, sans_serif).

    import matplotlib.font_manager as fm

    ft: Any = None
    try:
        # We'll use matplotlib's font inspection module to inspect font tables if it's available
        import matplotlib.ft2font as ft
    except ImportError:
        pass

    serif_fonts: set[str] = set()
    sans_serif_fonts: set[str] = set()

    def record_font(name: str, category: FontCategory) -> bool:
        if category == FontCategory.SERIF:
            dest = serif_fonts
        elif category == FontCategory.SANS_SERIF:
            dest = sans_serif_fonts
        else:
            return False

        dest.add(name)
        return True

    # 1. Scan Matplotlib's known font entries (ttflist)
    for entry in getattr(fm.fontManager, "ttflist", []):
        name = entry.name
        # First, try a fast name-based classification (standard families, explicit 'sans'/'serif')
        if record_font(name, classify_font_name(name, include_keywords=False)):
            continue

        # Next, check file-level OpenType table / FreeType inspection
        fname = getattr(entry, "fname", None)
        if fname:
            classification = _classify_font_file(fname, ft)
            if classification is not None and record_font(name, classification[1]):
                continue

        # If everything else has failed, fall back to matching keywords.
        record_font(name, classify_font_name(name, include_keywords=True))

    # 2. Scan any remaining font family names from font manager
    try:
        all_font_names = set(fm.get_font_names())
    except (OSError, RuntimeError):
        all_font_names = set()

    for name in all_font_names:
        if name not in serif_fonts and name not in sans_serif_fonts:
            record_font(name, classify_font_name(name, include_keywords=True))

    return serif_fonts, sans_serif_fonts


def _resolve_font_types(
    serif: bool | None, sans_serif: bool | None
) -> tuple[bool, bool]:
    # Resolve (serif, sans_serif) filter flags into (include_serif, include_sans_serif).
    if serif is False and sans_serif is False:
        return False, False
    if serif is None and sans_serif is None:
        return True, True
    if serif is not None and sans_serif is not None:
        return serif, sans_serif
    if serif is not None:
        return serif, not serif
    assert sans_serif is not None
    return not sans_serif, sans_serif


def get_fonts(
    latex: bool | None = None,
    serif: bool | None = None,
    sans_serif: bool | None = None,
    pattern: str
    | re.Pattern[str]
    | list[str | re.Pattern[str]]
    | tuple[str | re.Pattern[str], ...]
    | None = None,
) -> list[str]:
    """Return a list of available fonts for matplotlib to use.

    Args:
        latex: If True, return only fonts available in LaTeX.
            If False, return only fonts available without LaTeX.
            If None, return both LaTeX and non-LaTeX fonts.
            If LaTeX is not available on the system, the LaTeX fonts list is empty.
        serif: Filter for serif fonts. If None (default), its value is inferred from sans_serif.
        sans_serif: Filter for sans-serif fonts. If None (default), its value is inferred from serif.
        pattern: Optional pattern or list of patterns (str or re.Pattern) to match
            font names against. If a list of patterns is provided, each pattern is
            matched in turn.

    Returns:
        list[str]: Filtered list of font names available for matplotlib.

    Raises:
        ImportError: If 'matplotlib' is not installed.
        TypeError: If latex, serif, sans_serif, or pattern arguments have invalid types.
    """
    try:
        import matplotlib.font_manager  # noqa: F401
    except ImportError as err:
        raise ImportError(
            "The 'matplotlib' package is required for plot functionality. "
            "Please install it using 'pip install matplotlib' or 'pip install pygmentation[plots]'."
        ) from err

    # Check arguments
    if latex is not None and not isinstance(latex, bool):
        raise TypeError(
            f"Expected latex to be bool or None, got {type(latex).__name__}"
        )
    if serif is not None and not isinstance(serif, bool):
        raise TypeError(
            f"Expected serif to be bool or None, got {type(serif).__name__}"
        )
    if sans_serif is not None and not isinstance(sans_serif, bool):
        raise TypeError(
            f"Expected sans_serif to be bool or None, got {type(sans_serif).__name__}"
        )

    # Normalise `pattern` to a list of compiles `re.Pattern`s
    pattern_list: list[str | re.Pattern[str]] | None = None
    if pattern is not None:
        if isinstance(pattern, (str, re.Pattern)):
            pattern_list = [pattern]
        elif isinstance(pattern, (list, tuple)):
            pattern_list = list(pattern)
            for p in pattern_list:
                if not isinstance(p, (str, re.Pattern)):
                    raise TypeError(
                        f"Pattern elements must be str or re.Pattern, got {type(p).__name__}"
                    )
        else:
            raise TypeError(
                f"Expected pattern to be str, re.Pattern, list, or None, got {type(pattern).__name__}"
            )

    include_serif, include_sans_serif = _resolve_font_types(serif, sans_serif)
    if not include_serif and not include_sans_serif:
        return []

    result_fonts: set[str] = set()

    # Collect LaTeX fonts if requested and available
    if latex is not False:
        if is_latex_available():
            latex_serif, latex_sans = _get_latex_fonts()
            if include_serif:
                result_fonts.update(latex_serif)
            if include_sans_serif:
                result_fonts.update(latex_sans)

    # Collect non-LaTeX fonts if requested
    if latex is not True:
        non_latex_serif, non_latex_sans = _get_non_latex_fonts()
        if include_serif:
            result_fonts.update(non_latex_serif)
        if include_sans_serif:
            result_fonts.update(non_latex_sans)

    base_fonts = sorted(result_fonts)

    if pattern_list is None:
        return base_fonts

    regexes = [
        re.compile(p, re.IGNORECASE) if isinstance(p, str) else p for p in pattern_list
    ]
    return [f for regex in regexes for f in base_fonts if regex.search(f)]
