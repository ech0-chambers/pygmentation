"""Unit tests for scheme exporters in pygmentation.exporters."""

import shutil
import subprocess
from pathlib import Path
import pytest

from pygmentation import ColorScheme, SchemeType
from pygmentation.exporters import (
    CssExporter,
    Exporter,
    JavascriptExporter,
    LatexExporter,
    LessExporter,
    get_exporter,
)


def test_get_exporter_lookup():
    # By format name
    assert get_exporter("latex") is LatexExporter
    assert get_exporter("css") is CssExporter
    assert get_exporter("less") is LessExporter
    assert get_exporter("javascript") is JavascriptExporter

    # By extension
    assert get_exporter(".tex") is LatexExporter
    assert get_exporter(".sty") is LatexExporter
    assert get_exporter(".css") is CssExporter
    assert get_exporter(".less") is LessExporter
    assert get_exporter(".js") is JavascriptExporter

    # By aliases
    assert get_exporter("js") is JavascriptExporter
    assert get_exporter("less.js") is LessExporter
    assert get_exporter(".less.js") is LessExporter

    # Unknown
    assert get_exporter(".unknown") is None
    assert get_exporter("unknown_format") is None


def test_less_exporter_output(sample_nord_scheme):
    exporter = LessExporter()
    output = exporter.export(sample_nord_scheme)

    # Variable declarations
    assert "@clr-foreground: #ECEFF4;" in output
    assert "@clr-foreground-1: #" in output
    assert "@clr-foreground-5: #" in output

    assert "@clr-background: #2E3440;" in output
    assert "@clr-accent1: #5E81AC;" in output
    assert "@clr-accent1-1: #" in output

    assert f"@clr-surface1: #{sample_nord_scheme.surfaces[0].base.hex};" in output
    assert "@clr-auto_surface: #" in output

    # Aliases reference @clr targets without var()
    assert "@clr-red: @clr-accent4;" in output
    assert "@clr-red-1: @clr-accent4-1;" in output
    assert "@clr-purple: @clr-accent8;" in output
    assert "@clr-magenta: @clr-accent8;" in output
    assert "@clr-error: @clr-accent4;" in output
    assert "@clr-success: @clr-accent7;" in output


def test_javascript_exporter_output(sample_nord_scheme):
    exporter = JavascriptExporter()
    output = exporter.export(sample_nord_scheme)

    # Const declaration
    assert output.startswith("const colors = {")
    assert "foreground: {" in output
    assert 'base: "#ECEFF4",' in output
    assert '0: "#ECEFF4",' in output
    assert '1: "#' in output
    assert '5: "#' in output
    assert "variants: [" in output

    assert "background: {" in output
    assert 'base: "#2E3440",' in output

    assert "accents: [" in output
    assert "surfaces: [" in output
    assert "auto_surface: {" in output

    # Object definition closed before alias statements
    assert "};" in output

    # Aliases are assigned as object references
    assert "colors.red = colors.accents[3];" in output
    assert "colors.orange = colors.accents[4];" in output
    assert "colors.yellow = colors.accents[5];" in output
    assert "colors.green = colors.accents[6];" in output
    assert "colors.cyan = colors.accents[8];" in output
    assert "colors.blue = colors.accents[0];" in output
    assert "colors.purple = colors.accents[7];" in output
    assert "colors.magenta = colors.accents[7];" in output

    # Functional aliases
    assert "colors.error = colors.accents[3];" in output
    assert "colors.warning = colors.accents[5];" in output
    assert "colors.success = colors.accents[6];" in output
    assert "colors.info = colors.accents[0];" in output


def test_javascript_execution_in_node(sample_nord_scheme):
    if not shutil.which("node"):
        pytest.skip("Node.js is not installed on this system.")

    exporter = JavascriptExporter()
    code = exporter.export(sample_nord_scheme)

    # Append test assertions evaluated directly by Node.js
    test_harness = (
        code
        + "\n"
        + """
// 1. Structure mimicry
console.assert(colors.foreground.base === "#ECEFF4", "fg base");
console.assert(colors.foreground[0] === "#ECEFF4", "fg 0");
console.assert(typeof colors.foreground[1] === "string", "fg 1");
console.assert(colors.background.base === "#2E3440", "bg base");

console.assert(Array.isArray(colors.accents), "accents is array");
console.assert(colors.accents.length === 9, "accents length");
console.assert(typeof colors.accents[3][1] === "string", "accents[3][1]");
console.assert(colors.accents[3][0] === colors.accents[3].base, "accents[3][0] is base");
console.assert(Array.isArray(colors.accents[3].variants), "accents[3].variants is array");

console.assert(Array.isArray(colors.surfaces), "surfaces is array");
console.assert(typeof colors.auto_surface.base === "string", "auto_surface base");

// 2. Aliases are references (strict equality ===)
console.assert(colors.red === colors.accents[3], "red is reference to accents[3]");
console.assert(colors.red.base === colors.accents[3].base, "red.base");
console.assert(colors.red[1] === colors.accents[3][1], "red[1]");
console.assert(colors.error === colors.accents[3], "error is reference to accents[3]");
console.assert(colors.error === colors.red, "error is reference to red");
console.assert(colors.purple === colors.accents[7], "purple is reference to accents[7]");
console.assert(colors.magenta === colors.accents[7], "magenta is reference to accents[7]");
console.assert(colors.purple === colors.magenta, "purple is reference to magenta");
"""
    )

    proc = subprocess.run(
        ["node", "-e", test_harness],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Node.js error: {proc.stderr}"


def test_less_compilation(sample_nord_scheme):
    if not shutil.which("npx"):
        pytest.skip("npx is not available to run lessc.")

    exporter = LessExporter()
    less_code = exporter.export(sample_nord_scheme)

    # Append CSS rule utilizing the exported Less variables
    test_less = (
        less_code
        + "\n.test { color: @clr-red; background: @clr-background; border: 1px solid @clr-accent1-1; }\n"
    )

    proc = subprocess.run(
        ["npx", "--yes", "less", "-"],
        input=test_less,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Less compilation failed: {proc.stderr}"
    assert "color: #BF616A;" in proc.stdout
    assert "background: #2E3440;" in proc.stdout


def test_base_exporter_helpers():
    assert Exporter.canonical_name("foreground", None) == "foreground"
    assert Exporter.canonical_name("accents", 0) == "accents0"
    assert Exporter.canonical_name("surfaces", 2) == "surfaces2"
    assert Exporter.canonical_alias_name("red") == "red"


def test_latex_exporter_methods(sample_nord_scheme):
    exporter = LatexExporter()
    assert exporter.format_name == "latex"
    assert ".tex" in exporter.file_extensions

    assert exporter.canonical_name("foreground", None) == "Foregroundcolour"
    assert exporter.canonical_name("background", None) == "Backgroundcolour"
    assert exporter.canonical_name("accents", 0) == "Accent1"
    assert exporter.canonical_name("surfaces", 0) == "Surface1"
    assert exporter.canonical_name("auto_surface", None) == "AutoSurface"
    assert exporter.canonical_alias_name("red") == "Red"

    # Formatting methods
    color = sample_nord_scheme.accents[3].base
    assert exporter.format_color(color, "Accent4") == rf"\definecolor{{Accent4}}{{HTML}}{{{color.hex}}}"
    assert exporter.format_alias("Red", "Accent4") == r"\colorlet{Red}{Accent4}"

    fam_lines = exporter.format_family(sample_nord_scheme.foreground, "Foregroundcolour")
    assert len(fam_lines) == 6
    assert fam_lines[0].startswith(r"\definecolor{Foregroundcolour}{HTML}{")
    assert fam_lines[1].startswith(r"\definecolor{Foregroundcolour_1}{HTML}{")

    alias_fam_lines = exporter.format_alias_family("Red", "Accent4")
    assert len(alias_fam_lines) == 6
    assert alias_fam_lines[0] == r"\colorlet{Red}{Accent4}"
    assert alias_fam_lines[1] == r"\colorlet{Red_1}{Accent4_1}"


def test_latex_exporter_output(sample_nord_scheme):
    exporter = LatexExporter()
    output = exporter.export(sample_nord_scheme)

    assert r"\definecolor{Foregroundcolour}{HTML}{" in output
    assert r"\definecolor{Backgroundcolour}{HTML}{" in output
    assert r"\definecolor{Accent1}{HTML}{" in output
    assert r"\definecolor{Surface1}{HTML}{" in output
    assert r"\definecolor{AutoSurface}{HTML}{" in output
    assert r"\colorlet{Red}{Accent4}" in output
    assert r"\colorlet{Error}{Accent4}" in output


def test_latex_exporter_save(sample_nord_scheme, tmp_path):
    tex_path = tmp_path / "nord.tex"
    exporter = LatexExporter()
    exporter.save(sample_nord_scheme, tex_path)

    assert tex_path.exists()
    content = tex_path.read_text(encoding="utf-8")
    assert r"\definecolor{Foregroundcolour}{HTML}{" in content
    assert r"\colorlet{Red}{Accent4}" in content


def test_css_exporter_methods(sample_nord_scheme):
    exporter = CssExporter()
    assert exporter.format_name == "css"
    assert ".css" in exporter.file_extensions

    assert exporter.canonical_name("foreground", None) == "--clr-foreground"
    assert exporter.canonical_name("accents", 0) == "--clr-accent1"
    assert exporter.canonical_name("surfaces", 0) == "--clr-surface1"
    assert exporter.canonical_alias_name("red") == "--clr-red"

    color = sample_nord_scheme.accents[3].base
    formatted_color = exporter.format_color(color, "--clr-accent4")
    assert f"--clr-accent4: #{color.hex};" in formatted_color
    assert f"--clr-accent4-rgb: {color.r}, {color.g}, {color.b};" in formatted_color

    formatted_alias = exporter.format_alias("--clr-red", "--clr-accent4")
    assert "--clr-red: var(--clr-accent4);" in formatted_alias
    assert "--clr-red-rgb: var(--clr-accent4-rgb);" in formatted_alias


def test_css_exporter_output(sample_nord_scheme):
    exporter = CssExporter()
    output = exporter.export(sample_nord_scheme)

    assert output.startswith(":root{\n")
    assert output.endswith("\n}")
    assert "--clr-foreground: #" in output
    assert "--clr-background: #" in output
    assert "--clr-accent1: #" in output
    assert "--clr-surface1: #" in output
    assert "--clr-auto_surface: #" in output
    assert "--clr-red: var(--clr-accent4);" in output
    assert "--clr-error: var(--clr-accent4);" in output


def test_css_exporter_save_string_path(sample_nord_scheme, tmp_path):
    css_path = str(tmp_path / "nord.css")
    exporter = CssExporter()
    exporter.save(sample_nord_scheme, css_path)

    p = Path(css_path)
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert ":root{" in content
    assert "--clr-foreground:" in content


def test_exporter_save_method(sample_nord_scheme, tmp_path):
    js_path = tmp_path / "nord.js"
    exporter = JavascriptExporter()
    exporter.save(sample_nord_scheme, js_path)

    assert js_path.exists()
    content = js_path.read_text()
    assert content.startswith("const colors = {")
    assert "colors.red = colors.accents[3];" in content
