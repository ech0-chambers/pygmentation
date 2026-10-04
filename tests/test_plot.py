"""Unit tests for matplotlib plot styling integration in pygmentation.plot."""

from pathlib import Path
import re
from unittest.mock import MagicMock, patch
import pytest

from pygmentation import ColorScheme, SchemeType
from pygmentation.exceptions import SchemeNotFoundError
from pygmentation.plot import (
    DocType,
    FontCategory,
    KNOWN_LATEX_PACKAGES,
    _classify_font_file,
    _clean_tex_directory,
    _get_latex_fonts,
    _get_non_latex_fonts,
    _get_tex_font_directories,
    _get_texmf_roots,
    _kpsewhich_target_exists,
    _resolve_font_types,
    _resolve_latex_package_from_path,
    classify_font_name,
    apply_plot_styles,
    get_fonts,
    init,
    init_matplotlib,
    is_latex_available,
)
from pygmentation.registry import registry

try:
    import cycler  # noqa: F401
    import matplotlib.pyplot  # noqa: F401
    HAS_PLOT_DEPS = True
except ImportError:
    HAS_PLOT_DEPS = False

requires_plots = pytest.mark.skipif(
    not HAS_PLOT_DEPS,
    reason="Requires optional 'plots' dependencies ('matplotlib' and 'cycler')",
)


def test_doctype_enum():
    assert DocType.REPORT == 1
    assert DocType.PRESENTATION == 2
    assert DocType["REPORT"] is DocType.REPORT
    assert DocType["PRESENTATION"] is DocType.PRESENTATION


def test_is_latex_available():
    with patch("shutil.which") as mock_which:
        mock_which.side_effect = lambda cmd: "/usr/bin/" + cmd if cmd == "latex" else None
        assert is_latex_available() is True

        mock_which.side_effect = lambda cmd: "/usr/bin/" + cmd if cmd == "pdflatex" else None
        assert is_latex_available() is True

        mock_which.side_effect = lambda cmd: None
        assert is_latex_available() is False


def test_init_aliases():
    assert init is apply_plot_styles
    assert init_matplotlib is apply_plot_styles


def test_init_missing_cycler_dependency():
    with patch.dict("sys.modules", {"cycler": None}):
        with pytest.raises(ImportError, match="The 'cycler' package is required"):
            apply_plot_styles("nord")


def test_init_missing_matplotlib_dependency():
    mock_cycler = MagicMock()
    with patch.dict("sys.modules", {"cycler": mock_cycler, "matplotlib.pyplot": None}):
        with pytest.raises(ImportError, match="The 'matplotlib' package is required"):
            apply_plot_styles("nord")


@requires_plots
def test_init_report_styling(sample_nord_scheme):
    with patch("pygmentation.plot.fonts.is_latex_available", return_value=True):
        params = apply_plot_styles(sample_nord_scheme, doc_type="report")

    assert params["font.size"] == 12
    assert params["figure.figsize"] == (6.4, 4.8)
    assert params["figure.dpi"] == 300
    assert params["axes.spines.top"] is True
    assert params["axes.spines.right"] is True
    assert params["text.color"] == sample_nord_scheme.foreground.css
    assert params["axes.edgecolor"] == sample_nord_scheme.foreground.css
    assert params["axes.labelcolor"] == sample_nord_scheme.foreground.css
    assert params["xtick.color"] == sample_nord_scheme.foreground.css
    assert params["ytick.color"] == sample_nord_scheme.foreground.css
    assert params["figure.facecolor"] == sample_nord_scheme.background.base.css
    assert params["axes.facecolor"] == sample_nord_scheme.background.base.css
    assert params["legend.edgecolor"] == sample_nord_scheme.foreground.css
    assert params["legend.facecolor"] == sample_nord_scheme.background[5].css
    assert params["legend.framealpha"] == 0.5
    assert params["legend.fancybox"] is True
    assert params["text.usetex"] is True

    # Prop cycle check
    cycle_list = list(params["axes.prop_cycle"])
    distinct = sample_nord_scheme.distinct
    assert len(cycle_list) == len(distinct) * 3
    assert cycle_list[0]["color"] == distinct[0].base.css
    assert cycle_list[0]["linestyle"] == "-"
    assert cycle_list[len(distinct)]["linestyle"] == "--"
    assert cycle_list[len(distinct) * 2]["linestyle"] == ":"


@requires_plots
def test_init_presentation_styling(sample_nord_scheme):
    params = apply_plot_styles(sample_nord_scheme, doc_type=DocType.PRESENTATION)

    assert params["font.size"] == 16
    assert params["figure.figsize"] == (8, 4.5)
    assert params["axes.spines.top"] is False
    assert params["axes.spines.right"] is False
    assert params["figure.facecolor"] == sample_nord_scheme.background.base.css
    assert params["axes.facecolor"] == sample_nord_scheme.background.base.css

    first_distinct_css = sample_nord_scheme.distinct[0].css
    assert params["axes.edgecolor"] == first_distinct_css
    assert params["axes.labelcolor"] == first_distinct_css
    assert params["xtick.color"] == first_distinct_css
    assert params["ytick.color"] == first_distinct_css


@requires_plots
def test_init_transparent_flag(sample_nord_scheme):
    params_report = apply_plot_styles(sample_nord_scheme, doc_type="report", transparent=True)
    assert params_report["figure.facecolor"] == "none"
    assert params_report["axes.facecolor"] == "none"

    params_pres = apply_plot_styles(sample_nord_scheme, doc_type="presentation", transparent=True)
    assert params_pres["figure.facecolor"] == "none"
    assert params_pres["axes.facecolor"] == "none"


@requires_plots
def test_init_string_scheme_resolution():
    params = apply_plot_styles(scheme="nord", scheme_type="dark", doc_type="report")
    scheme = registry.get("nord", SchemeType.DARK)

    assert params["text.color"] == scheme.foreground.css
    assert params["axes.facecolor"] == scheme.background.base.css


@requires_plots
def test_init_invalid_arguments():
    with pytest.raises(SchemeNotFoundError):
        apply_plot_styles("completely_unknown_scheme_name_xyz")

    with pytest.raises(ValueError, match="Invalid scheme_type"):
        apply_plot_styles("nord", scheme_type="invalid_type")

    with pytest.raises(ValueError, match="Invalid doc_type"):
        apply_plot_styles("nord", doc_type="invalid_doc")

    with pytest.raises(TypeError, match="Expected scheme name"):
        apply_plot_styles(12345)


@requires_plots
def test_init_use_latex_option(sample_nord_scheme):
    # Explicit use_latex=True
    params_latex = apply_plot_styles(sample_nord_scheme, use_latex=True)
    assert params_latex["text.usetex"] is True
    assert "text.latex.preamble" in params_latex

    # Explicit use_latex=False
    params_no_latex = apply_plot_styles(sample_nord_scheme, use_latex=False)
    assert params_no_latex["text.usetex"] is False
    assert "text.latex.preamble" not in params_no_latex

    # use_latex=None (default) auto-detection when compiler is available
    with patch("pygmentation.plot.fonts.is_latex_available", return_value=True):
        params_auto_true = apply_plot_styles(sample_nord_scheme)
        assert params_auto_true["text.usetex"] is True
        assert "text.latex.preamble" in params_auto_true

    # use_latex=None (default) auto-detection when compiler is unavailable
    with patch("pygmentation.plot.fonts.is_latex_available", return_value=False):
        params_auto_false = apply_plot_styles(sample_nord_scheme)
        assert params_auto_false["text.usetex"] is False
        assert "text.latex.preamble" not in params_auto_false


@requires_plots
def test_init_font_options(sample_nord_scheme):
    # Custom font_family and font_serif
    params = apply_plot_styles(
        sample_nord_scheme,
        font_family="sans-serif",
        font_serif="Georgia",
        font_sans_serif="Arial",
    )
    assert params["font.family"] == "sans-serif"
    assert params["font.serif"] == "Georgia"
    assert params["font.sans-serif"] == "Arial"


@requires_plots
def test_init_only_font_given(sample_nord_scheme):
    # "If only font is given, it should be used for both other font arguments."
    params = apply_plot_styles(sample_nord_scheme, font="Helvetica")
    assert params["font.serif"] == "Helvetica"
    assert params["font.sans-serif"] == "Helvetica"


@requires_plots
def test_init_font_with_partial_overrides(sample_nord_scheme):
    # font with font_serif override preserves font_serif and sets font_sans_serif to font
    params = apply_plot_styles(sample_nord_scheme, font="Helvetica", font_serif="Times")
    assert params["font.serif"] == "Times"
    assert params["font.sans-serif"] == "Helvetica"

    # font with font_sans_serif override preserves font_sans_serif and sets font_serif to font
    params2 = apply_plot_styles(sample_nord_scheme, font="Times", font_sans_serif="Arial")
    assert params2["font.serif"] == "Times"
    assert params2["font.sans-serif"] == "Arial"


def test_get_fonts_missing_matplotlib_dependency():
    with patch.dict("sys.modules", {"matplotlib.font_manager": None}):
        with pytest.raises(ImportError, match="The 'matplotlib' package is required"):
            get_fonts()


@requires_plots
def test_get_fonts_invalid_argument_types():
    with pytest.raises(TypeError, match="Expected latex to be bool or None"):
        get_fonts(latex="true")  # type: ignore

    with pytest.raises(TypeError, match="Expected serif to be bool or None"):
        get_fonts(serif=1)  # type: ignore

    with pytest.raises(TypeError, match="Expected sans_serif to be bool or None"):
        get_fonts(sans_serif="no")  # type: ignore


@requires_plots
def test_get_fonts_both_false_returns_empty():
    assert get_fonts(serif=False, sans_serif=False) == []
    assert get_fonts(latex=True, serif=False, sans_serif=False) == []
    assert get_fonts(latex=False, serif=False, sans_serif=False) == []
    assert get_fonts(latex=None, serif=False, sans_serif=False) == []


@requires_plots
def test_get_fonts_latex_available():
    mock_serif = {"Computer Modern Roman", "Times"}
    mock_sans = {"Fira Sans", "Helvetica"}
    with patch("pygmentation.plot.fonts.is_latex_available", return_value=True):
        with patch("pygmentation.plot.fonts._get_latex_fonts", return_value=(mock_serif, mock_sans)):
            # Only serif
            serif_fonts = get_fonts(latex=True, serif=True, sans_serif=False)
            assert serif_fonts == sorted(mock_serif)

            # Only sans-serif
            sans_fonts = get_fonts(latex=True, serif=False, sans_serif=True)
            assert sans_fonts == sorted(mock_sans)

            # Both True
            both_true = get_fonts(latex=True, serif=True, sans_serif=True)
            assert both_true == sorted(mock_serif | mock_sans)

            # Both None (default)
            both_none = get_fonts(latex=True)
            assert both_none == both_true


@requires_plots
def test_get_fonts_latex_unavailable():
    with patch("pygmentation.plot.fonts.is_latex_available", return_value=False):
        assert get_fonts(latex=True) == []
        assert get_fonts(latex=True, serif=True) == []
        assert get_fonts(latex=True, sans_serif=True) == []


@requires_plots
def test_get_fonts_filter_rules_latex():
    mock_serif = {"Computer Modern Roman", "Times"}
    mock_sans = {"Fira Sans", "Helvetica"}
    expected_serif = sorted(mock_serif)
    expected_sans = sorted(mock_sans)
    expected_both = sorted(mock_serif | mock_sans)

    with patch("pygmentation.plot.fonts.is_latex_available", return_value=True):
        with patch("pygmentation.plot.fonts._get_latex_fonts", return_value=(mock_serif, mock_sans)):
            # If only one is True: include only that type
            assert get_fonts(latex=True, serif=True, sans_serif=None) == expected_serif
            assert get_fonts(latex=True, serif=None, sans_serif=True) == expected_sans

            # If only one is False: exclude only that type
            assert get_fonts(latex=True, serif=False, sans_serif=None) == expected_sans
            assert get_fonts(latex=True, serif=None, sans_serif=False) == expected_serif

            # If both are True or both are None: include both types
            assert get_fonts(latex=True, serif=True, sans_serif=True) == expected_both
            assert get_fonts(latex=True, serif=None, sans_serif=None) == expected_both


@requires_plots
def test_get_fonts_dynamic_latex_fonts():
    # Verify dynamic detection on actual system when LaTeX is available
    if is_latex_available():
        serif_fonts = get_fonts(latex=True, serif=True, sans_serif=False)
        assert "Computer Modern Roman" in serif_fonts

        sans_fonts = get_fonts(latex=True, serif=False, sans_serif=True)
        assert len(sans_fonts) > 0
        assert "Computer Modern Sans Serif" in sans_fonts
        if "Fira Sans" in sans_fonts:
            assert "Fira Sans" in sans_fonts


def test_get_texmf_roots_no_kpsewhich():
    with patch("shutil.which", return_value=None):
        _get_texmf_roots.cache_clear()
        assert _get_texmf_roots() == []
        _get_texmf_roots.cache_clear()


def test_get_texmf_roots_parsing(tmp_path):
    root1 = tmp_path / "texmf-dist"
    root2 = tmp_path / "texmf-local"
    root3 = tmp_path / "texmf-var"
    sub_root = root1 / "sub"
    for r in (root1, root2, root3, sub_root):
        r.mkdir(parents=True)
    nonexistent = tmp_path / "nonexistent"

    def mock_subprocess_run(cmd, **kwargs):
        mock_res = MagicMock()
        arg = cmd[1]
        if arg == "-var-value=TEXMF":
            # Simulate composite TEXMF variable with curly braces, '!' modifiers, and separators
            mock_res.stdout = f"{{!{root1}//,{root2};{nonexistent}}}"
        elif "TEXMFSYSVAR" in arg:
            mock_res.stdout = f"!{root3}/"
        elif "TEXMFDIST" in arg:
            mock_res.stdout = str(sub_root)
        else:
            mock_res.stdout = ""
        return mock_res

    _get_texmf_roots.cache_clear()
    try:
        with patch("shutil.which", return_value="/usr/bin/kpsewhich"):
            with patch("subprocess.run", side_effect=mock_subprocess_run):
                roots = _get_texmf_roots()
                # Should contain all existing roots and exclude nonexistent
                assert str(root1.resolve()) in roots
                assert str(root2.resolve()) in roots
                assert str(root3.resolve()) in roots
                assert str(sub_root.resolve()) in roots
                assert str(nonexistent) not in roots

                # Should be sorted longest-first (most path parts first)
                for i in range(len(roots) - 1):
                    assert len(Path(roots[i]).parts) >= len(Path(roots[i + 1]).parts)
    finally:
        _get_texmf_roots.cache_clear()


def test_get_texmf_roots_subprocess_error():
    import subprocess

    def mock_run_error(cmd, **kwargs):
        raise subprocess.SubprocessError("kpsewhich error")

    _get_texmf_roots.cache_clear()
    try:
        with patch("shutil.which", return_value="/usr/bin/kpsewhich"):
            with patch("subprocess.run", side_effect=mock_run_error):
                assert _get_texmf_roots() == []
    finally:
        _get_texmf_roots.cache_clear()


def test_get_tex_font_directories_no_kpsewhich():
    with patch("shutil.which", return_value=None):
        _get_texmf_roots.cache_clear()
        _get_tex_font_directories.cache_clear()
        assert _get_tex_font_directories() == []
        _get_texmf_roots.cache_clear()
        _get_tex_font_directories.cache_clear()


def test_clean_tex_directory(tmp_path):
    # Non-existent directory
    assert _clean_tex_directory(str(tmp_path / "nonexistent")) is None

    # Empty string or dot
    assert _clean_tex_directory("") is None
    assert _clean_tex_directory(".") is None

    # Directory without 'tex' in path returns None (regardless of existence)
    assert _clean_tex_directory("/usr/share/fonts/truetype") is None

    # Directory with 'tex' in path, with leading '!' and trailing slashes
    tex_dir = tmp_path / "texmf-dist" / "fonts"
    tex_dir.mkdir(parents=True)
    raw_unix = f"!{tex_dir}//"
    res = _clean_tex_directory(raw_unix)
    assert res == tex_dir.resolve()

    raw_win = f"!{tex_dir}\\\\"
    res_win = _clean_tex_directory(raw_win)
    assert res_win == tex_dir.resolve()


def test_get_tex_font_directories_parsing(tmp_path):
    tex_dir = tmp_path / "texmf" / "fonts" / "opentype"
    tex_dir.mkdir(parents=True)
    texmf_dist = tmp_path / "texmf-dist"
    (texmf_dist / "fonts" / "truetype").mkdir(parents=True)

    def mock_subprocess_run(cmd, **kwargs):
        mock_res = MagicMock()
        arg = cmd[1]
        if arg.startswith("-show-path="):
            mock_res.stdout = f"!{tex_dir}//:/nonexistent/tex/path"
        elif arg.startswith("-var-value="):
            if "TEXMFDIST" in arg:
                mock_res.stdout = str(texmf_dist)
            else:
                mock_res.stdout = ""
        return mock_res

    _get_texmf_roots.cache_clear()
    _get_tex_font_directories.cache_clear()
    try:
        with patch("shutil.which", return_value="/usr/bin/kpsewhich"):
            with patch("subprocess.run", side_effect=mock_subprocess_run):
                dirs = _get_tex_font_directories()
                assert str(tex_dir.resolve()) in dirs
                assert str((texmf_dist / "fonts" / "truetype").resolve()) in dirs
    finally:
        _get_texmf_roots.cache_clear()
        _get_tex_font_directories.cache_clear()


@requires_plots
def test_get_fonts_non_latex():
    # Non-LaTeX fonts query system fonts via matplotlib
    non_latex_all = get_fonts(latex=False)
    assert len(non_latex_all) > 0

    non_latex_serif = get_fonts(latex=False, serif=True, sans_serif=False)
    assert len(non_latex_serif) > 0
    assert "DejaVu Serif" in non_latex_serif
    assert "DejaVu Sans" not in non_latex_serif

    non_latex_sans = get_fonts(latex=False, serif=False, sans_serif=True)
    assert len(non_latex_sans) > 0
    assert "DejaVu Sans" in non_latex_sans
    assert "DejaVu Serif" not in non_latex_sans


@requires_plots
def test_get_fonts_latex_none():
    # When LaTeX is available, latex=None returns both LaTeX and non-LaTeX fonts
    with patch("pygmentation.plot.fonts.is_latex_available", return_value=True):
        fonts_both_sources = get_fonts(latex=None, serif=True, sans_serif=False)
        assert "Computer Modern Roman" in fonts_both_sources
        assert "DejaVu Serif" in fonts_both_sources

    # When LaTeX is unavailable, latex=None returns only non-LaTeX fonts (LaTeX list is empty)
    with patch("pygmentation.plot.fonts.is_latex_available", return_value=False):
        fonts_no_latex = get_fonts(latex=None, serif=True, sans_serif=False)
        assert "Computer Modern Roman" not in fonts_no_latex
        assert "DejaVu Serif" in fonts_no_latex
        assert fonts_no_latex == get_fonts(latex=False, serif=True, sans_serif=False)


@requires_plots
def test_get_non_latex_fonts_edge_cases():
    import matplotlib.font_manager as fm

    bad_entry = MagicMock()
    bad_entry.name = "CorruptedFont"
    bad_entry.fname = "/path/to/corrupt.ttf"

    _get_non_latex_fonts.cache_clear()
    try:
        with patch("matplotlib.ft2font.FT2Font", side_effect=RuntimeError("Corrupt font file")):
            with patch.object(fm.fontManager, "ttflist", [bad_entry]):
                with patch("matplotlib.font_manager.get_font_names", return_value=["CorruptedFont", "ExtraSerifFont", "ExtraSansFont"]):
                    serifs, sans = _get_non_latex_fonts()
                    assert "ExtraSerifFont" in serifs
                    assert "ExtraSansFont" in sans
    finally:
        _get_non_latex_fonts.cache_clear()


@requires_plots
def test_font_list_caching():
    # Verify non-LaTeX font caching
    _get_non_latex_fonts.cache_clear()
    info0 = _get_non_latex_fonts.cache_info()
    assert info0.hits == 0 and info0.misses == 0

    fonts1 = get_fonts(latex=False)
    info1 = _get_non_latex_fonts.cache_info()
    assert info1.misses == 1 and info1.hits == 0

    fonts2 = get_fonts(latex=False)
    info2 = _get_non_latex_fonts.cache_info()
    assert info2.misses == 1 and info2.hits == 1
    assert fonts1 == fonts2

    get_fonts(latex=False, pattern="DejaVu")
    info3 = _get_non_latex_fonts.cache_info()
    assert info3.misses == 1 and info3.hits == 2

    # Verify LaTeX font caching
    if is_latex_available():
        _get_latex_fonts.cache_clear()
        info_l0 = _get_latex_fonts.cache_info()
        assert info_l0.hits == 0 and info_l0.misses == 0

        l_fonts1 = get_fonts(latex=True)
        info_l1 = _get_latex_fonts.cache_info()
        assert info_l1.misses == 1 and info_l1.hits == 0

        l_fonts2 = get_fonts(latex=True)
        info_l2 = _get_latex_fonts.cache_info()
        assert info_l2.misses == 1 and info_l2.hits == 1
        assert l_fonts1 == l_fonts2

        get_fonts(latex=True, pattern="Fira")
        info_l3 = _get_latex_fonts.cache_info()
        assert info_l3.misses == 1 and info_l3.hits == 2


@requires_plots
def test_get_fonts_pattern_single_string():
    res = get_fonts(pattern="Fira")
    assert isinstance(res, list)
    assert len(res) > 0
    assert all("fira" in f.lower() for f in res)


@requires_plots
def test_get_fonts_pattern_compiled_regex():
    res = get_fonts(pattern=re.compile(r"^DejaVu Sans$"))
    assert isinstance(res, list)
    assert res == ["DejaVu Sans"]


@requires_plots
def test_get_fonts_pattern_list_matching_in_turn():
    # get_fonts(pattern=[a, b, c]) == get_fonts(pattern=a) + get_fonts(pattern=b) + get_fonts(pattern=c)
    res_a = get_fonts(pattern="Fira")
    res_b = get_fonts(pattern="DejaVu")
    res_combined = get_fonts(pattern=["Fira", "DejaVu"])

    assert isinstance(res_combined, list)
    assert res_combined == res_a + res_b


@requires_plots
def test_get_fonts_pattern_empty_or_single_result():
    # Empty match returns an empty list
    empty_res = get_fonts(pattern="nonexistent_pattern_string_xyz_123")
    assert isinstance(empty_res, list)
    assert empty_res == []

    # Single match returns a list with length 1
    single_res = get_fonts(pattern=re.compile(r"^DejaVu Serif$"))
    assert isinstance(single_res, list)
    assert len(single_res) == 1
    assert single_res == ["DejaVu Serif"]


@requires_plots
def test_get_fonts_pattern_invalid_types():
    with pytest.raises(TypeError, match="Expected pattern to be str, re.Pattern, list, or None"):
        get_fonts(pattern=123)  # type: ignore

    with pytest.raises(TypeError, match="Pattern elements must be str or re.Pattern"):
        get_fonts(pattern=["Valid", 123])  # type: ignore


@requires_plots
def test_get_latex_fonts_returns_dict_pair():
    serif_dict, sans_dict = _get_latex_fonts()
    assert isinstance(serif_dict, dict)
    assert isinstance(sans_dict, dict)

    # Classic fonts should map to None
    assert "Computer Modern Roman" in serif_dict
    assert serif_dict["Computer Modern Roman"] is None

    # Known TeX packages mapping check
    assert KNOWN_LATEX_PACKAGES["Fira Sans"] == "FiraSans"
    assert KNOWN_LATEX_PACKAGES["Source Sans Pro"] == "sourcesanspro"
    assert KNOWN_LATEX_PACKAGES["Kurier"] == "kurier"


def test_get_latex_fonts_latex_unavailable():
    _get_latex_fonts.cache_clear()
    try:
        with patch("pygmentation.plot.fonts.is_latex_available", return_value=False):
            serif_dict, sans_dict = _get_latex_fonts()
            assert serif_dict == {}
            assert sans_dict == {}
    finally:
        _get_latex_fonts.cache_clear()


def test_resolve_latex_package_from_path(tmp_path):
    # Non-TDS path returns None
    assert _resolve_latex_package_from_path("/tmp/not_tds/font.ttf", "Font") is None

    # Construct mock TDS hierarchy: <root>/fonts/opentype/public/myfont/...
    texmf = tmp_path / "texmf"
    font_dir = texmf / "fonts" / "opentype" / "public" / "myfont"
    font_dir.mkdir(parents=True)
    font_file = str(font_dir / "MyFont-Regular.otf")

    latex_dir = texmf / "tex" / "latex" / "myfont"
    latex_dir.mkdir(parents=True)

    # Missing .sty returns None
    assert _resolve_latex_package_from_path(font_file, "My Font") is None

    # 1. Exact match with cleaned family name (case-insensitive)
    sty_named = latex_dir / "MyFont.sty"
    sty_named.touch()
    assert _resolve_latex_package_from_path(font_file, "My Font") == "MyFont"
    sty_named.unlink()

    # 2. Match with package directory name
    sty_pkg = latex_dir / "myfont.sty"
    sty_pkg.touch()
    assert _resolve_latex_package_from_path(font_file, "Some Font") == "myfont"
    sty_pkg.unlink()

    # 3. Single .sty in directory
    sty_single = latex_dir / "custom_pkg.sty"
    sty_single.touch()
    assert _resolve_latex_package_from_path(font_file, "Unrelated Name") == "custom_pkg"

    # Path containing multiple 'fonts' segments (e.g. /home/fonts_user/repo/texmf/fonts/opentype/...)
    multi_fonts_dir = tmp_path / "fonts_folder" / "texmf" / "fonts" / "opentype" / "public" / "pkg"
    multi_fonts_dir.mkdir(parents=True)
    multi_font_file = str(multi_fonts_dir / "Pkg-Regular.otf")
    multi_latex_dir = tmp_path / "fonts_folder" / "texmf" / "tex" / "latex" / "pkg"
    multi_latex_dir.mkdir(parents=True)
    (multi_latex_dir / "pkg.sty").touch()
    assert _resolve_latex_package_from_path(multi_font_file, "Pkg") == "pkg"

    # Case-insensitive directory matching fallback (capitalized font dir, lowercase latex dir)
    case_dir = tmp_path / "texmf2" / "fonts" / "opentype" / "public" / "CamelCase"
    case_dir.mkdir(parents=True)
    case_file = str(case_dir / "Font.otf")
    case_latex_dir = tmp_path / "texmf2" / "tex" / "latex" / "camelcase"
    case_latex_dir.mkdir(parents=True)
    (case_latex_dir / "camelcase.sty").touch()
    assert _resolve_latex_package_from_path(case_file, "CamelCase") == "camelcase"

    # Prefix matching via explicit texmf_roots parameter and via mocked _get_texmf_roots()
    (latex_dir / "myfont.sty").touch()
    assert _resolve_latex_package_from_path(font_file, "My Font", texmf_roots=[str(texmf)]) == "myfont"
    with patch("pygmentation.plot.fonts._get_texmf_roots", return_value=[str(texmf)]):
        assert _resolve_latex_package_from_path(font_file, "My Font") == "myfont"
    (latex_dir / "myfont.sty").unlink()


@requires_plots
def test_apply_plot_styles_preamble_package_injection(sample_nord_scheme):
    mock_serif = {"Times": None, "XCharter": "XCharter"}
    mock_sans = {"Fira Sans": "FiraSans", "Helvetica": None}

    with patch("pygmentation.plot.fonts._get_latex_fonts", return_value=(mock_serif, mock_sans)):
        # 1. Classic font (Times): No package injected into preamble
        params_classic = apply_plot_styles(
            sample_nord_scheme,
            use_latex=True,
            font_family="serif",
            font_serif="Times",
        )
        assert params_classic["text.latex.preamble"] == r"\usepackage{amsmath, amssymb}"

        # 2. Modern font (Fira Sans): Package \usepackage{FiraSans} injected
        params_modern = apply_plot_styles(
            sample_nord_scheme,
            use_latex=True,
            font_family="sans-serif",
            font_sans_serif="Fira Sans",
        )
        assert r"\usepackage{amsmath, amssymb}" in params_modern["text.latex.preamble"]
        assert r"\usepackage{FiraSans}" in params_modern["text.latex.preamble"]

        # 3. Both serif and sans modern fonts specified: both packages loaded
        params_both = apply_plot_styles(
            sample_nord_scheme,
            use_latex=True,
            font_family="serif",
            font_serif="XCharter",
            font_sans_serif="Fira Sans",
        )
        assert r"\usepackage{XCharter}" in params_both["text.latex.preamble"]
        assert r"\usepackage{FiraSans}" in params_both["text.latex.preamble"]

        # 4. font parameter sets both: package loaded without duplicates
        params_font = apply_plot_styles(
            sample_nord_scheme,
            use_latex=True,
            font="Fira Sans",
        )
        preamble = params_font["text.latex.preamble"]
        assert preamble.count(r"\usepackage{FiraSans}") == 1


@requires_plots
def test_get_fonts_with_dict_return():
    mock_serif = {"Times": None, "XCharter": "XCharter"}
    mock_sans = {"Fira Sans": "FiraSans", "Helvetica": None}

    with patch("pygmentation.plot.fonts.is_latex_available", return_value=True):
        with patch("pygmentation.plot.fonts._get_latex_fonts", return_value=(mock_serif, mock_sans)):
            fonts = get_fonts(latex=True)
            # Must return a list of font name strings
            assert isinstance(fonts, list)
            assert fonts == sorted(["Times", "XCharter", "Fira Sans", "Helvetica"])


def test_classify_font_file():
    # If ft_module is None, return None
    assert _classify_font_file("/dummy/path.otf", None) is None

    mock_ft = MagicMock()

    # If FT2Font raises RuntimeError, OSError, or ValueError, return None
    mock_ft.FT2Font.side_effect = RuntimeError("Broken font")
    assert _classify_font_file("/dummy/path.otf", mock_ft) is None

    mock_ft.FT2Font.side_effect = OSError("Access denied")
    assert _classify_font_file("/dummy/path.otf", mock_ft) is None

    mock_ft.FT2Font.side_effect = ValueError("Invalid format")
    assert _classify_font_file("/dummy/path.otf", mock_ft) is None

    # Empty family name returns None
    mock_font = MagicMock()
    mock_font.family_name = "   "
    mock_ft.FT2Font.side_effect = None
    mock_ft.FT2Font.return_value = mock_font
    assert _classify_font_file("/dummy/path.otf", mock_ft) is None

    # Name contains "sans" -> sans-serif (FontCategory.SANS_SERIF)
    mock_font.family_name = "Custom Sans Font"
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("Custom Sans Font", FontCategory.SANS_SERIF)

    # Name contains "serif" -> serif (FontCategory.SERIF)
    mock_font.family_name = "Custom Serif Font"
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("Custom Serif Font", FontCategory.SERIF)

    # OS/2 table panose classification
    mock_font.family_name = "AmbiguousFont"
    mock_font.get_sfnt_table.return_value = {"panose": (2, 11)}
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("AmbiguousFont", FontCategory.SANS_SERIF)

    mock_font.get_sfnt_table.return_value = {"panose": (2, 4)}
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("AmbiguousFont", FontCategory.SERIF)

    # OS/2 table sFamilyClass classification
    mock_font.get_sfnt_table.return_value = {"panose": None, "sFamilyClass": 8 << 8}
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("AmbiguousFont", FontCategory.SANS_SERIF)

    mock_font.get_sfnt_table.return_value = {"panose": None, "sFamilyClass": 1 << 8}
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("AmbiguousFont", FontCategory.SERIF)

    # Keyword fallback
    mock_font.get_sfnt_table.return_value = None
    mock_font.family_name = "Fira Code"
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("Fira Code", FontCategory.SANS_SERIF)

    mock_font.family_name = "Garamond Premier"
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("Garamond Premier", FontCategory.SERIF)

    # Unclassified
    mock_font.family_name = "UnknownStyle"
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("UnknownStyle", FontCategory.UNCLASSIFIED)

    # get_sfnt_table raises KeyError
    mock_font.get_sfnt_table.side_effect = KeyError("No OS/2 table")
    assert _classify_font_file("/dummy/path.otf", mock_ft) == ("UnknownStyle", FontCategory.UNCLASSIFIED)
    mock_font.get_sfnt_table.side_effect = None


def test_font_category_enum():
    assert FontCategory.SERIF == "serif"
    assert FontCategory.SANS_SERIF == "sans-serif"
    assert FontCategory.UNCLASSIFIED == "unclassified"
    assert isinstance(FontCategory.SERIF, str)
    assert FontCategory("serif") is FontCategory.SERIF
    assert FontCategory("sans-serif") is FontCategory.SANS_SERIF
    assert FontCategory("unclassified") is FontCategory.UNCLASSIFIED


def test_kpsewhich_target_exists():
    import subprocess

    with patch("subprocess.run") as mock_run:
        # Success with stdout
        mock_run.return_value = MagicMock(stdout="/path/to/font.tfm\n")
        assert _kpsewhich_target_exists("font.tfm") is True

        # Success with empty stdout
        mock_run.return_value = MagicMock(stdout="  \n")
        assert _kpsewhich_target_exists("font.tfm") is False

        # TimeoutExpired / SubprocessError returns False
        mock_run.side_effect = subprocess.TimeoutExpired(["kpsewhich"], 2)
        assert _kpsewhich_target_exists("font.tfm") is False

        # OSError returns False
        mock_run.side_effect = OSError("Permission denied")
        assert _kpsewhich_target_exists("font.tfm") is False


def test_classify_font_name():
    # Standard Matplotlib names
    assert classify_font_name("DejaVu Serif") == FontCategory.SERIF
    assert classify_font_name("dejavu serif") == FontCategory.SERIF
    assert classify_font_name("DejaVu Sans") == FontCategory.SANS_SERIF
    assert classify_font_name("Helvetica") == FontCategory.SANS_SERIF

    # Explicit tokens without keywords
    assert classify_font_name("Custom Sans Font", include_keywords=False) == FontCategory.SANS_SERIF
    assert classify_font_name("Custom Serif Font", include_keywords=False) == FontCategory.SERIF
    assert classify_font_name("Garamond Premier", include_keywords=False) == FontCategory.UNCLASSIFIED

    # Keyword fallback
    assert classify_font_name("Garamond Premier", include_keywords=True) == FontCategory.SERIF
    assert classify_font_name("Fira Code", include_keywords=True) == FontCategory.SANS_SERIF
    assert classify_font_name("CompletelyUnknownStyle", include_keywords=True) == FontCategory.UNCLASSIFIED


def test_resolve_font_types():
    assert _resolve_font_types(False, False) == (False, False)
    assert _resolve_font_types(None, None) == (True, True)
    assert _resolve_font_types(True, True) == (True, True)
    assert _resolve_font_types(True, False) == (True, False)
    assert _resolve_font_types(False, True) == (False, True)
    assert _resolve_font_types(True, None) == (True, False)
    assert _resolve_font_types(False, None) == (False, True)
    assert _resolve_font_types(None, True) == (False, True)
    assert _resolve_font_types(None, False) == (True, False)







