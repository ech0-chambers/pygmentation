import argparse
from pathlib import Path
from typing import Any, Callable

from rich.console import Console
from rich.text import Text

from .colors.scheme import ColorFamily, ColorScheme
from .registry import registry
from .exceptions import SchemeNotFoundError

# Formatter mappings for color code representations (e.g. hex, rgb, hsl, hsv, Lab)
show_code_map: dict[str, Callable[[Any], str]] = {}

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
    parser = argparse.ArgumentParser(prog = "pygmentation", description = "A command-line tool for generating and managing color schemes.")
    subparsers = parser.add_subparsers(dest = "command", required = True)

    def add_scheme_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("scheme", help = "The name of the scheme to use")
        parser.add_argument("variant", nargs = "?", default = "both", choices = ["both", "light", "dark"], help = "The variant of the scheme to use (default: both)")

    def add_code_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-s", "--show-codes", action = "store_true", help = "Include the color codes for the scheme")
        parser.add_argument("-c", "--code-type", choices = ["hex", "rgb", "hsl", "hsv", "Lab"], help = "The format of color codes to show (default: hex)")

    def add_file_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-f", "--filename", required = True, help = "The path to the output file")

    # show
    show_parser = subparsers.add_parser("show", help = "Show a scheme in the terminal, optionally only showing the light or dark variant (default: both)")
    add_scheme_args(show_parser)
    add_code_args(show_parser)

    # save
    save_parser = subparsers.add_parser("save", help = "Save a .svg file of a scheme, optionally only saving the light or dark variant (default: both)")
    add_scheme_args(save_parser)
    add_code_args(save_parser)
    add_file_args(save_parser)
    
    # write
    write_parser = subparsers.add_parser("write", help = "Write a .tex, .css, .tcss (textual css), or .js file of a scheme, optionally only saving the light or dark variant (default: both)")
    add_scheme_args(write_parser)
    add_file_args(write_parser)
    write_parser.add_argument("-t", "--type", choices = ["latex", "css", "tcss", "js"], help = "The type of file to write (default: inferred from filename extension)")

    # list
    list_parser = subparsers.add_parser("list", help = "List all available schemes, with a sample of each. If pattern is provided, only schemes matching the pattern are listed (accepts standard shell wildcards)")
    list_parser.add_argument("--names-only", action = "store_true", help = "Just print the names of the schemes with no sample")
    list_parser.add_argument("pattern", nargs = "?", default = "*", help = "A pattern to match against scheme names (default: *)")
    list_parser.add_argument("variant", nargs = "?", default = "light", choices = ["light", "dark"], help = "The variant of the schemes to list (default: light)")

    return parser.parse_args(argv)


def resolve_unknown_scheme(
    requested: str
) -> str | None:
    """Prompt the user with fuzzy-matched scheme candidates; returns chosen scheme name or None."""
    pass


def multiple_choice_prompt(prompt: str, choices: list[str], default: int = 1) -> int:
    """Interactive numbered selection prompt helper using Rich IntPrompt."""
    pass


def square(col: ColorFamily, variant: int | None = None) -> Text:
    """Format a unicode block swatch (█████) styled with the specified color."""
    pass


def show_scheme(
    scheme: ColorScheme,
    name: str | None = None,
    save: bool = False,
    filepath: Path | str | None = None,
    show_codes: bool = False,
    code_type: str = "hex",
) -> None:
    """Generate and print a compact Rich panel displaying the color scheme in the terminal."""
    pass


def show_scheme_wide(
    scheme: ColorScheme,
    name: str | None = None,
    save: bool = False,
    filepath: Path | str | None = None,
    show_codes: bool = False,
    code_type: str = "hex",
) -> None:
    """Generate and print a wide two-column Rich panel for terminals with width >= 112."""
    pass


def cli_show(
    scheme_name: str,
    variant: str = "both",
    show_codes: bool = False,
    code_type: str = "hex",
) -> None:
    """Command handler for 'pygmentation show': loads and displays scheme in the terminal."""
    pass


def cli_save(
    filename: str | Path,
    scheme_name: str,
    variant: str = "both",
) -> None:
    """Command handler for 'pygmentation save': exports scheme preview to SVG via Rich."""
    pass


def cli_write(
    filename: str | Path,
    scheme_name: str,
    variant: str = "both",
    filetype: str | None = None,
) -> None:
    """Command handler for 'pygmentation write': writes exported color definitions (.tex, .css, .js, etc.)."""
    pass


def cli_list(
    names_only: bool = False,
    pattern: str = "*",
    variant: str = "light",
) -> None:
    """Command handler for 'pygmentation list': lists available schemes with optional swatch preview table."""
    pass


def main(argv: list[str] | None = None) -> int:

    args = parse_args(argv)

    if args.command == "list":
        # handle list first, since everything else requires a valid scheme
        return 0

    if registry.has_scheme(args.scheme):
        scheme_name = args.scheme
    else:
        resolved = resolve_unknown_scheme(args.scheme)
        if not resolved:
            error(f"Unknown scheme '{args.scheme}'.")
            return 1
        scheme_name = resolved

    if args.command == "show":
        cli_show(scheme_name, args.variant, args.show_codes, args.code_type)
        return 0

    if args.command == "save":
        cli_save(scheme_name, args.variant, args.filename, args.show_codes, args.code_type)
        return 0

    if args.command == "write":
        cli_write(args.filename, scheme_name, args.variant, args.type)
        return 0


