import argparse
import difflib
import io
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rich import box
from rich.color import Color as RichColor
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.style import Style
from rich.table import Table
from rich.text import Text

from .colors.scheme import Color, ColorFamily, ColorScheme, SchemeType
from .exporters import SvgExporter, get_exporter
from .registry import registry

# Formatter mappings for color code representations (e.g. hex, rgb, hsl, hsv, Lab)
show_code_map: dict[str, Callable[[Any], str]] = {
    "hex": lambda c: c.hex,
    "rgb": lambda c: f"{c.as_255.r}, {c.as_255.g}, {c.as_255.b}",
    "hsl": lambda c: f"{c.h:.0f}°, {c.s * 100:.0f}%, {c.l * 100:.0f}%",
    "hsv": lambda c: f"{c.hsv.h:.0f}°, {c.hsv.s * 100:.0f}%, {c.hsv.v * 100:.0f}%",
    "lab": lambda c: f"{c.lab.l:.0f}, {c.lab.a:.0f}, {c.lab.b:.0f}",
    "xyz": lambda c: f"{c.xyz.x:.0f}, {c.xyz.y:.0f}, {c.xyz.z:.0f}",
    "oklab": lambda c: f"{c.oklab.l:.2f}, {c.oklab.a:.2f}, {c.oklab.b:.2f}",
    "oklch": lambda c: f"{c.oklch.l:.2f}, {c.oklch.c:.2f}, {c.oklch.h:.0f}°",
}

default_console = Console()


def get_console(console: Console | None = None) -> Console:
    return console if console is not None else default_console


def error(message: str, console: Console | None = None) -> None:
    console = get_console(console)
    console.print(f"[bold red]Error:[/bold red] {message}")


def warning(message: str, console: Console | None = None) -> None:
    console = get_console(console)
    console.print(f"[bold orange]Warning:[/bold orange] {message}")


def success(message: str, console: Console | None = None) -> None:
    console = get_console(console)
    console.print(f"[bold green]Success:[/bold green] {message}")


def info(message: str, console: Console | None = None) -> None:
    console = get_console(console)
    console.print(f"[bold blue]Info:[/bold blue] {message}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pygmentation",
        description="A command-line tool for generating and managing color schemes.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_scheme_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("scheme", help="The name of the scheme to use")
        parser.add_argument(
            "variant",
            nargs="?",
            default="both",
            choices=["both", "light", "dark"],
            help="The variant of the scheme to use (default: both)",
        )

    def add_code_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-s",
            "--show-codes",
            action="store_true",
            help="Include the color codes for the scheme",
        )
        parser.add_argument(
            "-c",
            "--code-type",
            choices=["hex", "rgb", "hsl", "hsv", "lab", "xyz", "oklab", "oklch"],
            help="The format of color codes to show (default: hex)",
        )

    def add_file_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-f", "--filename", required=True, help="The path to the output file"
        )

    # show
    show_parser = subparsers.add_parser(
        "show",
        help="Show a scheme in the terminal, optionally only showing the light or dark variant (default: both)",
    )
    add_scheme_args(show_parser)
    add_code_args(show_parser)

    # save
    save_parser = subparsers.add_parser(
        "save",
        help="Save a .svg file of a scheme, optionally only saving the light or dark variant (default: both)",
    )
    add_scheme_args(save_parser)
    add_code_args(save_parser)
    add_file_args(save_parser)

    # write
    write_parser = subparsers.add_parser(
        "write",
        help="Write a .tex, .css, .tcss (textual css), or .js file of a scheme, optionally only saving the light or dark variant (default: both)",
    )
    add_scheme_args(write_parser)
    add_file_args(write_parser)
    write_parser.add_argument(
        "-t",
        "--type",
        choices=["latex", "css", "tcss", "js", "less", "javascript"],
        help="The type of file to write (default: inferred from filename extension)",
    )

    # list
    list_parser = subparsers.add_parser(
        "list",
        help="List all available schemes, with a sample of each. If pattern is provided, only schemes matching the pattern are listed (accepts standard shell wildcards)",
    )
    list_parser.add_argument(
        "--names-only",
        action="store_true",
        help="Just print the names of the schemes with no sample",
    )
    list_parser.add_argument(
        "pattern",
        nargs="?",
        default=".*",
        help="A pattern to match against scheme names, accepts regex patterns (default: .*)",
    )
    list_parser.add_argument(
        "variant",
        nargs="?",
        default="light",
        choices=["light", "dark"],
        help="The variant of the schemes to list (default: light)",
    )

    return parser.parse_args(argv)


def resolve_unknown_scheme(requested: str) -> str | None:
    similar = difflib.get_close_matches(requested, registry.available)
    if len(similar) == 0:
        error(
            f"Unknown scheme '{requested}'. I could not find any schemes with similar names."
        )
        return None

    similar.append("None of the above (quit)")
    index = multiple_choice_prompt(
        f"Unknown scheme '{requested}'. Did you mean:", similar
    )
    if index == len(similar):
        # User selected "None of the above"
        return None
    return similar[index - 1]


def multiple_choice_prompt(
    prompt: str, choices: list[str], default: int = 1, console: Console | None = None
) -> int:
    console = get_console(console)
    console.print(prompt)
    for i, choice in enumerate(choices):
        console.print(
            f"[bold]{i + 1: >2d}[/bold]. {choice}"
            + (" [dim](default)[/dim]" if i == default - 1 else "")
        )

    response = IntPrompt.ask(f"Choose 1 to {len(choices)}", default=default)
    return response


def swatch(color: Color) -> Text:
    return Text("     \n     ", style=Style(bgcolor=RichColor.from_rgb(*color.as_255)))


def scheme_swatch(scheme: ColorScheme) -> Text:
    swatch = Text()
    swatch.append(
        "    ", style=Style(bgcolor=RichColor.from_rgb(*scheme.foreground.base.as_255))
    )
    swatch.append("  ")
    swatch.append(
        "    ", style=Style(bgcolor=RichColor.from_rgb(*scheme.background.base.as_255))
    )
    swatch.append("    ")
    for accent in scheme.accents:
        swatch.append("  ", style=Style(bgcolor=RichColor.from_rgb(*accent.base.as_255)))

    return swatch


def family_to_row(
    color_family: ColorFamily,
    name: str,
    name_color: Color,
    aliases: list[str],
    alias_color: Color,
    code_type: str | None = None,
) -> tuple[list[Any], list[Any] | None]:
    name_text = Text().append(
        name.capitalize() + ":\n",
        style=Style(color=RichColor.from_rgb(*name_color.as_255)),
    )
    for a in aliases:
        name_text.append(
            f"({a.capitalize()})\n",
            style=Style(color=RichColor.from_rgb(*alias_color.as_255)),
        )
    swatch_row = [
        name_text,
        swatch(color_family.base),
        "  ",
        *map(swatch, color_family[1:]),
    ]
    if code_type is not None:
        if code_type.lower() not in show_code_map:
            raise ValueError(
                f"Unrecognised code format {code_type}. This should be one of the following: {', '.join(show_code_map.keys())}"
            )
        code_func = show_code_map[code_type.lower()]
        code_row = [
            "",
            code_func(color_family.base),
            "",
            *map(code_func, color_family[1:]),
        ]
    else:
        code_row = None
    return swatch_row, code_row


def _get_aliases(scheme: ColorScheme, color_family: ColorFamily) -> list[str]:
    aliases = []
    for p in [
        "red",
        "orange",
        "yellow",
        "green",
        "cyan",
        "blue",
        "purple",
        "magenta",
    ]:
        alias_family = getattr(scheme, p, None)
        if alias_family is not None and alias_family.base == color_family.base:
            aliases.append(p)
    return aliases


def _build_scheme_sections(
    scheme: ColorScheme,
) -> list[list[tuple[str, ColorFamily, list[str]]]]:
    sections: list[list[tuple[str, ColorFamily, list[str]]]] = []

    # Section 1: Foreground & Background
    sections.append(
        [
            ("Foreground", scheme.foreground, []),
            ("Background", scheme.background, []),
        ]
    )

    # Section 2: Accents
    if scheme.accents:
        sections.append(
            [
                (f"Accent {i + 1}", accent, _get_aliases(scheme, accent))
                for i, accent in enumerate(scheme.accents)
            ]
        )

    # Section 3: Surfaces
    if scheme.surfaces:
        sections.append(
            [
                (f"Surface {i + 1}", surface, [])
                for i, surface in enumerate(scheme.surfaces)
            ]
        )

    # Section 4: Auto-surface
    if scheme.auto_surface is not None:
        sections.append([("Auto-surface", scheme.auto_surface, [])])

    return sections


def _build_scheme_table(
    scheme: ColorScheme,
    double: bool = False,
    code_type: str | None = None,
) -> Table:
    alias_color = (
        scheme.accents[0].base if scheme.accents else scheme.foreground.base
    )
    table = Table(
        show_header=True,
        header_style=Style(
            color=RichColor.from_rgb(*scheme.foreground.base.as_255), bold=True
        ),
        box=box.SIMPLE,
        leading=1,
        padding=0,
    )

    def add_headers() -> None:
        table.add_column("Colour", justify="right")
        table.add_column("Base", justify="center")
        table.add_column("", justify="center")
        for i in range(5):
            table.add_column(str(i + 1), justify="center")

    add_headers()
    if double:
        table.add_column("", justify="center")
        add_headers()

    sections = _build_scheme_sections(scheme)
    num_cols = 17 if double else 8

    first_section = True
    for section in sections:
        if not first_section:
            table.add_row(*[" "] * num_cols)
        first_section = False

        if double:
            for i in range(0, len(section), 2):
                l_name, l_family, l_aliases = section[i]
                l_swatches, l_codes = family_to_row(
                    l_family,
                    l_name,
                    scheme.foreground.base,
                    l_aliases,
                    alias_color,
                    code_type,
                )
                if i + 1 < len(section):
                    r_name, r_family, r_aliases = section[i + 1]
                    r_swatches, r_codes = family_to_row(
                        r_family,
                        r_name,
                        scheme.foreground.base,
                        r_aliases,
                        alias_color,
                        code_type,
                    )
                else:
                    r_swatches = [""] * 8
                    r_codes = [""] * 8 if code_type is not None else None

                table.add_row(*l_swatches, "  ", *r_swatches)
                if code_type is not None and l_codes is not None:
                    table.add_row(*l_codes, "  ", *r_codes)
        else:
            for name, family, aliases in section:
                swatches, codes = family_to_row(
                    family,
                    name,
                    scheme.foreground.base,
                    aliases,
                    alias_color,
                    code_type,
                )
                table.add_row(*swatches)
                if codes is not None:
                    table.add_row(*codes)

    return table


def show_scheme(
    scheme: ColorScheme,
    name: str | None = None,
    filepath: Path | str | None = None,
    code_type: str | None = None,
    console: Console | None = None,
) -> None:
    console = get_console(console)
    if name is None:
        name = "Colour Scheme"

    panel_style = Style(
        color=RichColor.from_rgb(*scheme.foreground.base.as_255),
        bgcolor=RichColor.from_rgb(*scheme.background.base.as_255),
    )

    # Construct the panel assuming a wide terminal, then measure and compare to the actual 
    # terminal width.
    double_table = _build_scheme_table(scheme, double=True, code_type=code_type)
    double_panel = Panel.fit(double_table, title=name, style=panel_style)

    measuring_console = Console(file=io.StringIO(), width=1000)
    double_width = measuring_console.measure(double_panel).maximum

    target_width = max(console.width, 300) if filepath is not None else console.width

    if target_width >= double_width:
        # We can use the double-width panel we just made
        panel = double_panel
    else:
        # We need to fall back to a single-width panel.
        single_table = _build_scheme_table(scheme, double=False, code_type=code_type)
        panel = Panel.fit(single_table, title=name, style=panel_style)

    if filepath is not None:
        # If we're saving to a file, measure the width so we can trim any extra space
        measured_width = measuring_console.measure(panel).maximum
        svg_console = Console(record=True, width=measured_width, file=io.StringIO())
        svg_console.print(panel)
        svg_console.save_svg(str(filepath), title=name)
    else:
        console.print(panel)


def cli_show(
    scheme_name: str,
    variant: str = "both",
    code_type: str | None = None,
) -> None:
    if variant in ["light", "both"]:
        scheme = registry.get(scheme_name, SchemeType.LIGHT)
        show_scheme(
            scheme, scheme_name + " (light)", filepath=None, code_type=code_type
        )
    if variant in ["dark", "both"]:
        scheme = registry.get(scheme_name, SchemeType.DARK)
        show_scheme(scheme, scheme_name + " (dark)", filepath=None, code_type=code_type)


def cli_save(
    filename: str | Path,
    scheme_name: str,
    variant: str = "both",
    code_type: str | None = None,
) -> None:
    filepath = Path(filename)
    if filepath.suffix != ".svg":
        raise ValueError(f"Filename must have a .svg extension, not {filepath.suffix}")
    if variant == "both":
        light_filepath = filepath.with_name(filepath.stem + "_light.svg")
        dark_filepath = filepath.with_name(filepath.stem + "_dark.svg")
    else:
        light_filepath = filepath
        dark_filepath = filepath

    svg_exporter = SvgExporter(code_type=code_type)

    if variant in ["light", "both"]:
        scheme = registry.get(scheme_name, SchemeType.LIGHT)
        # show_scheme(scheme, scheme_name + " (light)", light_filepath, code_type)
        svg_exporter.save(scheme, light_filepath)
    if variant in ["dark", "both"]:
        scheme = registry.get(scheme_name, SchemeType.DARK)
        # show_scheme(scheme, scheme_name + " (dark)", dark_filepath, code_type)
        svg_exporter.save(scheme, dark_filepath)


def cli_write(
    filename: str | Path,
    scheme_name: str,
    variant: str = "both",
    filetype: str | None = None,
) -> None:

    filepath = Path(filename)

    if filetype is None:
        filetype = filepath.suffix
    exporter_cls = get_exporter(filetype)
    if exporter_cls is None:
        raise ValueError(f"Could not find an exporter for files of type `{filetype}`")

    exporter = exporter_cls()

    if variant == "both":
        light_filepath = filepath.with_name(filepath.stem + "_light" + filepath.suffix)
        dark_filepath = filepath.with_name(filepath.stem + "_dark" + filepath.suffix)
    else:
        light_filepath = filepath
        dark_filepath = filepath

    if variant in ["light", "both"]:
        scheme = registry.get(scheme_name, SchemeType.LIGHT)
        exporter.save(scheme, light_filepath)
    if variant in ["dark", "both"]:
        scheme = registry.get(scheme_name, SchemeType.DARK)
        exporter.save(scheme, dark_filepath)


def get_schemes_by_pattern(pattern: str) -> list[str]:
    matches = [s for s in registry.available if re.search(pattern, s)]
    return matches


def cli_list(
    names_only: bool = False,
    pattern: str = ".*",
    variant: str = "light",
    console: Console | None = None,
) -> int:
    console = get_console(console)
    matches = get_schemes_by_pattern(pattern)
    if len(matches) == 0:
        print(f"No schemes match pattern `{pattern}`")
        return 1

    if names_only:
        for name in matches:
            print(name)
        return 0

    table = Table(show_lines=True)
    table.add_column("Name", justify="center")
    table.add_column("Sample", justify="left")
    for scheme_name in matches:
        scheme = registry.get(
            scheme_name, SchemeType.LIGHT if variant == "light" else SchemeType.DARK
        )
        table.add_row(
            Text(
                f" {scheme_name} ",
                style=f"bold {scheme.foreground.base.css} on {scheme.background.base.css}",
            ),
            scheme_swatch(scheme),
        )
    console.print(table)

    return 0


def main(argv: list[str] | None = None) -> int:

    args = parse_args(argv)

    if args.command == "list":
        result = cli_list(args.names_only, args.pattern, args.variant)
        return result

    if registry.has_scheme(args.scheme):
        scheme_name = args.scheme
    else:
        resolved = resolve_unknown_scheme(args.scheme)
        if not resolved:
            error(f"Unknown scheme '{args.scheme}'.")
            return 1
        scheme_name = resolved

    if args.command == "show":
        cli_show(scheme_name, args.variant, args.code_type)
        return 0

    if args.command == "save":
        cli_save(args.filename, scheme_name, args.variant, args.code_type)
        return 0

    if args.command == "write":
        cli_write(args.filename, scheme_name, args.variant, args.type)
        return 0

    return 0
