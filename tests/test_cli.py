"""Unit tests for the command line interface in pygmentation.cli."""

from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import pytest

from pygmentation import Color, ColorScheme, SchemeType
from pygmentation.cli import (
    _get_aliases,
    cli_list,
    cli_save,
    cli_show,
    cli_write,
    error,
    family_to_row,
    get_schemes_by_pattern,
    info,
    main,
    multiple_choice_prompt,
    parse_args,
    resolve_unknown_scheme,
    scheme_swatch,
    show_scheme,
    success,
    swatch,
    warning,
)
from pygmentation.registry import registry


# ============================================================================
# 1. Argument Parsing (parse_args)
# ============================================================================


def test_parse_args_show_defaults():
    args = parse_args(["show", "nord"])
    assert args.command == "show"
    assert args.scheme == "nord"
    assert args.variant == "both"
    assert args.show_codes is False
    assert args.code_type is None


def test_parse_args_show_options():
    args = parse_args(["show", "nord", "dark", "-s", "-c", "hex"])
    assert args.command == "show"
    assert args.scheme == "nord"
    assert args.variant == "dark"
    assert args.show_codes is True
    assert args.code_type == "hex"

    args_light = parse_args(["show", "nord", "light", "--show-codes", "--code-type", "rgb"])
    assert args_light.variant == "light"
    assert args_light.show_codes is True
    assert args_light.code_type == "rgb"


def test_parse_args_save_defaults():
    args = parse_args(["save", "nord", "-f", "out.svg"])
    assert args.command == "save"
    assert args.scheme == "nord"
    assert args.variant == "both"
    assert args.filename == "out.svg"
    assert args.show_codes is False
    assert args.code_type is None


def test_parse_args_save_options():
    args = parse_args(["save", "nord", "dark", "--filename", "palette.svg", "-s", "-c", "hsl"])
    assert args.command == "save"
    assert args.scheme == "nord"
    assert args.variant == "dark"
    assert args.filename == "palette.svg"
    assert args.show_codes is True
    assert args.code_type == "hsl"


def test_parse_args_write():
    args = parse_args(["write", "nord", "-f", "nord.tex"])
    assert args.command == "write"
    assert args.scheme == "nord"
    assert args.variant == "both"
    assert args.filename == "nord.tex"
    assert args.type is None

    args_typed = parse_args(["write", "nord", "light", "-f", "nord.js", "-t", "javascript"])
    assert args_typed.variant == "light"
    assert args_typed.filename == "nord.js"
    assert args_typed.type == "javascript"


def test_parse_args_list():
    args = parse_args(["list"])
    assert args.command == "list"
    assert args.names_only is False
    assert args.pattern == ".*"
    assert args.variant == "light"

    args_custom = parse_args(["list", "--names-only", "^nord", "dark"])
    assert args_custom.command == "list"
    assert args_custom.names_only is True
    assert args_custom.pattern == "^nord"
    assert args_custom.variant == "dark"


@pytest.mark.parametrize(
    "argv",
    [
        [],                                               # Missing subcommand
        ["unknown_command"],                              # Invalid subcommand
        ["save", "nord"],                                 # Missing required -f
        ["write", "nord"],                                # Missing required -f
        ["show", "nord", "neon"],                         # Invalid variant
        ["show", "nord", "-c", "cmyk"],                   # Invalid code_type
        ["write", "nord", "-f", "out.txt", "-t", "xyz"],  # Invalid exporter type
        ["list", ".*", "neon"],                           # Invalid variant for list
    ],
)
def test_parse_args_invalid_arguments(argv: list[str]):
    with pytest.raises(SystemExit):
        parse_args(argv)


# ============================================================================
# 2. Pattern Matching and cli_list
# ============================================================================


def test_get_schemes_by_pattern():
    matches = get_schemes_by_pattern("^nord")
    assert "nord" in matches
    assert "nord_terminal" in matches
    assert len(matches) >= 2

    all_matches = get_schemes_by_pattern(".*")
    assert len(all_matches) == len(registry.available)

    no_matches = get_schemes_by_pattern("^nonexistent_scheme_name_pattern$")
    assert no_matches == []


def test_cli_list_names_only(capsys):
    result = cli_list(names_only=True, pattern="^nord")
    assert result == 0
    captured = capsys.readouterr()
    lines = [line.strip() for line in captured.out.splitlines() if line.strip()]
    assert "nord" in lines
    assert "nord_terminal" in lines


def test_cli_list_rendered_table():
    result_light = cli_list(names_only=False, pattern="^nord", variant="light")
    assert result_light == 0

    result_dark = cli_list(names_only=False, pattern="^nord", variant="dark")
    assert result_dark == 0


def test_cli_list_no_matches(capsys):
    result = cli_list(pattern="^nonexistent_pattern_12345$")
    assert result == 1
    captured = capsys.readouterr()
    assert "No schemes match pattern" in captured.out


# ============================================================================
# 3. cli_show and Rich formatting helpers
# ============================================================================


@pytest.mark.parametrize("variant", ["both", "light", "dark"])
def test_cli_show_variants(variant: str):
    # Should execute without errors
    cli_show("nord", variant=variant)


@pytest.mark.parametrize("code_type", ["hex", "rgb", "hsl", "hsv", "lab", "Lab"])
def test_cli_show_code_types(code_type: str):
    cli_show("nord", variant="light", code_type=code_type)


def test_cli_show_invalid_code_type():
    with pytest.raises(ValueError, match="Unrecognised code format"):
        cli_show("nord", variant="light", code_type="cmyk")


def test_rich_formatting_helpers():
    c = Color("5E81AC")
    s = swatch(c)
    assert s.plain == "█████\n█████"

    scheme = registry.get("nord", SchemeType.DARK)
    ss = scheme_swatch(scheme)
    assert len(ss.plain) > 0

    # family_to_row with and without code_type
    swatches, codes = family_to_row(
        scheme.foreground,
        "Foreground",
        scheme.foreground.base,
        [],
        scheme.accents[0].base,
        code_type=None,
    )
    assert len(swatches) == 8
    assert codes is None

    swatches, codes = family_to_row(
        scheme.foreground,
        "Foreground",
        scheme.foreground.base,
        [],
        scheme.accents[0].base,
        code_type="hex",
    )
    assert len(codes) == 8
    assert codes[1] == scheme.foreground.base.hex

    aliases = _get_aliases(scheme, scheme.accents[0])
    assert isinstance(aliases, list)
    assert "blue" in aliases


def test_cli_logging_helpers():
    # Verify utility functions error, warning, success, info execute cleanly
    error("test error")
    warning("test warning")
    success("test success")
    info("test info")


# ============================================================================
# 4. cli_save
# ============================================================================


def test_cli_save_both_variants(tmp_path: Path):
    target = tmp_path / "nord_palette.svg"
    cli_save(target, "nord", variant="both")

    light_file = tmp_path / "nord_palette_light.svg"
    dark_file = tmp_path / "nord_palette_dark.svg"

    assert light_file.exists()
    assert dark_file.exists()

    light_content = light_file.read_text(encoding="utf-8")
    dark_content = dark_file.read_text(encoding="utf-8")

    assert "<svg" in light_content
    assert "</svg>" in light_content
    assert "<svg" in dark_content
    assert "</svg>" in dark_content


def test_cli_save_single_variant(tmp_path: Path):
    light_target = tmp_path / "nord_light_only.svg"
    cli_save(light_target, "nord", variant="light")
    assert light_target.exists()
    assert "<svg" in light_target.read_text(encoding="utf-8")

    dark_target = tmp_path / "nord_dark_only.svg"
    cli_save(dark_target, "nord", variant="dark", code_type="hex")
    assert dark_target.exists()
    assert "<svg" in dark_target.read_text(encoding="utf-8")


def test_cli_save_invalid_extension(tmp_path: Path):
    invalid_target = tmp_path / "nord_palette.png"
    with pytest.raises(ValueError, match=r"Filename must have a \.svg extension"):
        cli_save(invalid_target, "nord")


# ============================================================================
# 5. cli_write
# ============================================================================


@pytest.mark.parametrize("ext", [".tex", ".css", ".less", ".js"])
def test_cli_write_inferred_extension_both(tmp_path: Path, ext: str):
    target = tmp_path / f"export_test{ext}"
    cli_write(target, "nord", variant="both")

    light_file = tmp_path / f"export_test_light{ext}"
    dark_file = tmp_path / f"export_test_dark{ext}"

    assert light_file.exists()
    assert dark_file.exists()
    assert len(light_file.read_text(encoding="utf-8")) > 0
    assert len(dark_file.read_text(encoding="utf-8")) > 0


def test_cli_write_single_variant(tmp_path: Path):
    target = tmp_path / "single_export.css"
    cli_write(target, "nord", variant="light")
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "--clr-foreground:" in content


def test_cli_write_explicit_type(tmp_path: Path):
    target = tmp_path / "custom_filename.out"
    cli_write(target, "nord", variant="light", filetype="latex")
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert r"\definecolor" in content

    target_js = tmp_path / "custom_filename.bundle"
    cli_write(target_js, "nord", variant="dark", filetype="javascript")
    assert target_js.exists()
    js_content = target_js.read_text(encoding="utf-8")
    assert "const colors = {" in js_content


def test_cli_write_invalid_type(tmp_path: Path):
    target = tmp_path / "unsupported.xyz"
    with pytest.raises(ValueError, match="Could not find an exporter for files of type"):
        cli_write(target, "nord")


# ============================================================================
# 6. Unknown Scheme Recovery & Interactive Prompt
# ============================================================================


def test_multiple_choice_prompt():
    with patch("pygmentation.cli.IntPrompt.ask", return_value=2) as mock_ask:
        choice = multiple_choice_prompt("Select an option:", ["Option A", "Option B", "Option C"])
        assert choice == 2
        mock_ask.assert_called_once()


def test_resolve_unknown_scheme_selected():
    # Typing 'nort' should suggest 'nord'
    with patch("pygmentation.cli.multiple_choice_prompt", return_value=1):
        resolved = resolve_unknown_scheme("nort")
        assert resolved == "nord"


def test_resolve_unknown_scheme_none_of_above():
    # User selects the last option ("None of the above (quit)")
    def choose_last(prompt, choices, default=1):
        return len(choices)

    with patch("pygmentation.cli.multiple_choice_prompt", side_effect=choose_last):
        resolved = resolve_unknown_scheme("nort")
        assert resolved is None


def test_resolve_unknown_scheme_no_matches():
    resolved = resolve_unknown_scheme("completely_unmatched_scheme_name_99999")
    assert resolved is None


# ============================================================================
# 7. main() Entry Point & Return Codes
# ============================================================================


def test_main_list():
    assert main(["list"]) == 0
    assert main(["list", "--names-only", "^nord"]) == 0
    assert main(["list", "pattern_matching_nothing_xyz_12345"]) == 1


def test_main_show():
    assert main(["show", "nord", "dark", "-s", "-c", "hex"]) == 0


def test_main_save(tmp_path: Path):
    target = tmp_path / "main_out.svg"
    assert main(["save", "nord", "-f", str(target)]) == 0
    assert (tmp_path / "main_out_light.svg").exists()
    assert (tmp_path / "main_out_dark.svg").exists()


def test_main_write(tmp_path: Path):
    target = tmp_path / "main_out.tex"
    assert main(["write", "nord", "-f", str(target)]) == 0
    assert (tmp_path / "main_out_light.tex").exists()
    assert (tmp_path / "main_out_dark.tex").exists()


def test_main_unknown_scheme_resolved():
    # Scheme 'nort' resolved to 'nord' via mocked prompt
    with patch("pygmentation.cli.multiple_choice_prompt", return_value=1):
        assert main(["show", "nort"]) == 0


def test_main_unknown_scheme_cancelled():
    def choose_last(prompt, choices, default=1):
        return len(choices)

    with patch("pygmentation.cli.multiple_choice_prompt", side_effect=choose_last):
        assert main(["show", "nort"]) == 1


def test_main_unknown_scheme_no_suggestion():
    assert main(["show", "completely_unknown_scheme_name_99999"]) == 1


def test_module_execution():
    proc = subprocess.run(
        [sys.executable, "-m", "pygmentation", "list", "--names-only", "^nord"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "nord" in proc.stdout
    assert "nord_terminal" in proc.stdout
