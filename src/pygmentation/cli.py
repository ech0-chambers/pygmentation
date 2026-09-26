import argparse
from pathlib import Path
from typing import Any, Callable
import difflib
import re

from rich.console import Console
from rich.text import Text
from rich.style import Style
from rich.color import Color as RichColor
from rich.prompt import IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich import box

from .colors.scheme import SchemeType, Color, ColorFamily, ColorScheme
from .registry import registry
from .exceptions import SchemeNotFoundError
from .exporters import get_exporter

# Formatter mappings for color code representations (e.g. hex, rgb, hsl, hsv, Lab)
show_code_map: dict[str, Callable[[Any], str]] = {
    "hex": lambda c: c.hex,
    "rgb": lambda c: f"{c.r:.0f}, {c.g:.0f}, {c.b:.0f}",
    "hsl": lambda c: f"{c.h:.0f}, {c.s * 100:.0f}%, {c.l * 100:.0f}%",
    "hsv": lambda c: f"{c.hsv.h:.0f}, {c.hsv.s * 100:.0f}%, {c.hsv.v * 100:.0f}%",
    "lab": lambda c: f"{c.lab.l:.0f}, {c.lab.a:.0f}, {c.lab.b:.0f}",
}

console = Console()


def error(message: str) -> str:
    console.print(f"[bold red]Error:[/bold red] {message}")


def warning(message: str) -> str:
    console.print(f"[bold orange]Warning:[/bold orange] {message}")


def success(message: str) -> str:
    console.print(f"[bold green]Success:[/bold green] {message}")


def info(message: str) -> str:
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
            choices=["hex", "rgb", "hsl", "hsv", "Lab"],
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
        choices=["latex", "css", "tcss", "js"],
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
        f"Unknown scheme '{requested}. Did you mean:", similar
    )
    if index == len(similar):
        # User selected "None of the above"
        return None
    return similar[index - 1]


def multiple_choice_prompt(prompt: str, choices: list[str], default: int = 1) -> int:
    console.print(prompt)
    for i, choice in enumerate(choices):
        console.print(
            f"[bold]{i+1: >2d}[/bold]. {choice}"
            + (" [dim](default)[/dim]" if i == default - 1 else "")
        )

    response = IntPrompt.ask(f"Choose 1 to {len(choices)}", default=default)
    return response


def swatch(color: Color) -> Text:
    return Text("█████\n█████", style=Style(color=RichColor.from_rgb(*color.rgb)))

def scheme_swatch(scheme: ColorScheme) -> Text:
    swatch = Text()
    swatch.append("  ", style = Style(bgcolor=RichColor.from_rgb(*scheme.foreground.base.rgb)))
    swatch.append("  ", style = Style(bgcolor=RichColor.from_rgb(*scheme.background.base.rgb)))
    swatch.append("  ")
    for accent in scheme.accents:
        swatch.append("  ", style = Style(bgcolor=RichColor.from_rgb(*accent.base.rgb)))

    return swatch

def family_to_row(
    color_family: ColorFamily,
    name: str,
    name_color: Color,
    aliases: list[str],
    alias_color: Color,
    code_type: str | None = None,
) -> list[list[Text]]:
    name_text = Text().append(
        name.capitalize() + ":\n",
        style=Style(color=RichColor.from_rgb(*name_color.rgb)),
    )
    for a in aliases:
        name_text.append(
            f"({a.capitalize()})\n",
            style=Style(color=RichColor.from_rgb(*alias_color.rgb)),
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
                f"Unrecognised code format {code_type}. This should be one of the following: {", ".join(show_code_map.keys())}"
            )
        code_func = show_code_map[code_type]
        code_row = [
            "",
            code_func(color_family.base),
            "",
            *map(code_func, color_family[1:]),
        ]
    else:
        code_row = None
    return swatch_row, code_row

def _get_aliases(scheme, color_family):
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

def show_scheme(
    scheme: ColorScheme,
    name: str | None = None,
    filepath: Path | str | None = None,
    code_type: str | None = None,
) -> None:
    if name is None:
        name = "Colour Scheme"
    console.record = filepath is not None
    width = console.size.width
    # TODO: width decisions need a bit more thought if code_type is given.

    table = Table(show_header=False, box=box.SIMPLE, leading=1, padding=0)

    table.add_column("Name", justify="right")
    table.add_column("Base", justify="center")
    table.add_column("", justify="center")
    for i in range(5):
        table.add_column(str(i + 1), justify="center")

    rows = []

    rows.extend(family_to_row(
        scheme.foreground,
        "Foreground",
        scheme.foreground.base,
        [],
        scheme.accents[0].base,
        code_type,
    ))
    rows.extend(family_to_row(
        scheme.background,
        "Background",
        scheme.foreground.base,
        [],
        scheme.accents[0].base,
        code_type,
    ))
    # Accents
    rows.append([" "] * 8)
    for i, accent in enumerate(scheme.accents):
        aliases = _get_aliases(scheme, accent)
        rows.extend(family_to_row(
            accent,
            f"Accent {i+1}",
            scheme.foreground.base,
            aliases,
            scheme.accents[0].base,
            code_type
        ))
    # Surfaces
    if len(scheme.surfaces) > 0:
        rows.append([" "] * 8)
        for i, surface in enumerate(scheme.surfaces):
            rows.extend(family_to_row(
                surface,
                f"Surface {i+1}",
                scheme.foreground.base,
                [],
                scheme.accents[0].base,
                code_type
            ))
    # Auto-surfaces
    rows.append([" "] * 8)

    rows.extend(family_to_row(
        scheme.auto_surface,
        "Auto-Surface",
        scheme.foreground.base,
        [],
        scheme.accents[0].base,
        code_type
    ))

    rows = [r for r in rows if r]

    for row in rows:
        table.add_row(*row)

    panel = Panel.fit(
        table,
        title = name,
        style = Style(
            color = RichColor.from_rgb(*scheme.foreground.base.rgb),
            bgcolor = RichColor.from_rgb(*scheme.background.base.rgb),
        )
    )

    console.print(panel)
    if filepath is not None:
        console.save_svg(filepath)
        

def cli_show(
    scheme_name: str,
    variant: str = "both",
    code_type: str | None = None,
) -> None:
    if variant in ["light", "both"]:
        scheme = registry.get(scheme_name, SchemeType.LIGHT)
        show_scheme(scheme, scheme_name + " (light)", filepath = None, code_type=code_type)
    if variant in ["dark", "both"]:
        scheme = registry.get(scheme_name, SchemeType.DARK)
        show_scheme(scheme, scheme_name + " (dark)", filepath = None, code_type=code_type)

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

    if variant in ["light", "both"]:
        scheme = registry.get(scheme_name, SchemeType.LIGHT)
        show_scheme(scheme, scheme_name + " (light)", light_filepath, code_type)
    if variant in ["dark", "both"]:
        scheme = registry.get(scheme_name, SchemeType.DARK)
        show_scheme(scheme, scheme_name + " (dark)", dark_filepath, code_type)


def cli_write(
    filename: str | Path,
    scheme_name: str,
    variant: str = "both",
    filetype: str | None = None,
) -> None:
    
    filepath = Path(filename)

    if filetype is None:
        filetype = filepath.suffix
    exporter = get_exporter(filetype)
    if exporter is None:
        raise ValueError(f"Could not find an exporter for files of type `{filetype}`")

    exporter = exporter()

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
) -> int:
    matches = get_schemes_by_pattern(pattern)
    if len(matches) == 0:
        print(f"No schemes match pattern `{pattern}`")
        return 1

    if names_only:
        for scheme in matches: 
            print(scheme)
        return 0

    table = Table(show_lines = True)
    table.add_column("Name", justify = "center")
    table.add_column("Sample", justify = "center")
    for scheme_name in matches:
        scheme = registry.get(scheme_name, SchemeType.LIGHT if variant == "light" else SchemeType.DARK)
        table.add_row(
            Text(
                scheme_name,
                style = f"bold {scheme.foreground.base.css} on {scheme.background.base.css}"
            ),
            scheme_swatch(scheme)
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
        cli_save(
            args.filename, scheme_name, args.variant, args.code_type
        )
        return 0

    if args.command == "write":
        cli_write(args.filename, scheme_name, args.variant, args.type)
        return 0
