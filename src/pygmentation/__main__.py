import argparse
from pathlib import Path
import difflib
import re
from typing import List
from rich.console import Console
from rich.prompt import IntPrompt

def parse_args():
    # pygmentation show <scheme> [variant] -- Show a scheme in the terminal, optionally only showing the light or dark variant (default: both)
    # pygmentation save -f <filename> <scheme> [variant] -- Save a .svg file of a scheme, optionally only saving the light or dark variant (default: both)
    # pygmentation write -f <filename> -t <latex|css> <scheme> [variant] -- Write a .tex or .css file of a scheme, optionally only saving the light or dark variant (default: both). -t is optional, inferred from filename extension if not provided.
    # pygmentation list <pattern> -- List all available schemes, with a sample of each. If pattern is provided, only schemes matching the pattern are listed (accepts standard shell wildcards)

    parser = argparse.ArgumentParser(prog = "pygmentation", description = "A command-line tool for generating color schemes for quantum optics plots.")
    subparsers = parser.add_subparsers(dest = "command", required = True)

    show_parser = subparsers.add_parser("show", help = "Show a scheme in the terminal, optionally only showing the light or dark variant (default: both)")
    show_parser.add_argument("scheme", help = "The name of the scheme to show")
    show_parser.add_argument("variant", nargs = "?", default = "both", choices = ["both", "light", "dark"], help = "The variant of the scheme to show (default: both)")

    save_parser = subparsers.add_parser("save", help = "Save a .svg file of a scheme, optionally only saving the light or dark variant (default: both)")
    save_parser.add_argument("-f", "--filename", required = True, help = "The name of the file to save")
    save_parser.add_argument("scheme", help = "The name of the scheme to save")
    save_parser.add_argument("variant", nargs = "?", default = "both", choices = ["both", "light", "dark"], help = "The variant of the scheme to save (default: both)")

    write_parser = subparsers.add_parser("write", help = "Write a .tex or .css file of a scheme, optionally only saving the light or dark variant (default: both)")
    write_parser.add_argument("-f", "--filename", required = True, help = "The name of the file to save")
    write_parser.add_argument("-t", "--type", choices = ["latex", "css", "js"], help = "The type of file to write (default: inferred from filename extension)")
    write_parser.add_argument("scheme", help = "The name of the scheme to write")
    write_parser.add_argument("variant", nargs = "?", default = "both", choices = ["both", "light", "dark"], help = "The variant of the scheme to write (default: both)")

    list_parser = subparsers.add_parser("list", help = "List all available schemes, with a sample of each. If pattern is provided, only schemes matching the pattern are listed (accepts standard shell wildcards)")
    list_parser.add_argument("pattern", nargs = "?", default = "*", help = "A pattern to match against scheme names (default: *)")

    return parser.parse_args()


def handle_unknown_scheme(scheme_name: str) -> str:
    console = Console()
    similar = difflib.get_close_matches(scheme_name, get_available_schemes())
    if len(similar) == 0:
        console.print(f"Unknown scheme: {scheme_name}. I could not find any similar schemes.")
        quit(1)

    similar.append("None of the above (quit)")
    index = multiple_choice_prompt(f"Unknown scheme: {scheme_name}. Did you mean:", similar)
    if index == len(similar):
        quit(1)
    return similar[index - 1]

def multiple_choice_prompt(prompt: str, choices: List[str], default: int = 1) -> str:
    console = Console()
    console.print(prompt)
    for i, choice in enumerate(choices):
        console.print(f" [bold]{i+1: >2d}[/bold]. {choice}" + (" [dim](default)[/dim]" if i == default - 1 else ""))
    response = IntPrompt.ask(f"Choose 1 to {len(choices)}", default = default)
    return response



if __name__ == "__main__":
    from .pygmentation import show_scheme, set_scheme, get_scheme, get_available_schemes

    args = parse_args()
    available = get_available_schemes()

    if args.command != "list" and args.scheme not in available:
        args.scheme = handle_unknown_scheme(args.scheme)

    if args.command == "show":
        if args.variant in ["light", "both"]:
            set_scheme(args.scheme)
            show_scheme(name = f"{args.scheme} (light)")
        if args.variant in ["dark", "both"]:
            set_scheme(args.scheme, "dark")
            show_scheme(name = f"{args.scheme} (dark)")
    elif args.command == "save":
        filepath = Path(args.filename)
        if filepath.suffix != ".svg":
            raise ValueError("Filename must have .svg extension")
        if args.variant == "both":
            light_filepath = filepath.with_name(filepath.stem + "_light.svg")
            dark_filepath = filepath.with_name(filepath.stem + "_dark.svg")
            set_scheme(args.scheme, "light")
            show_scheme(name = f"{args.scheme} (light)", save = True, filepath = light_filepath)
            set_scheme(args.scheme, "dark")
            show_scheme(name = f"{args.scheme} (dark)", save = True, filepath = dark_filepath)
        else:
            set_scheme(args.scheme, args.variant)
            show_scheme(name = f"{args.scheme} ({args.variant})", save = True, filepath = filepath)
    elif args.command == "write":
        filepath = Path(args.filename)
        if args.type is not None:
            filetype = args.type
        elif filepath.suffix == ".tex":
            filetype = "latex"
        elif filepath.suffix == ".css":
            filetype = "css"
        elif filepath.suffix == ".js":
            filetype = "js"
        else:
            raise ValueError("Filename must have .tex, .css or .js extension, or type must be specified with -t/--type")
        
        if args.variant == "both":
            light_filepath = filepath.with_name(filepath.stem + "_light" + filepath.suffix)
            dark_filepath = filepath.with_name(filepath.stem + "_dark" + filepath.suffix)
            set_scheme(args.scheme, "light")
            with open(light_filepath, "w") as f:
                if filetype == "latex":
                    f.write(get_scheme().to_latex())
                elif filetype == "css":
                    f.write(get_scheme().to_css())
                elif filetype == "js":
                    f.write(get_scheme().to_javascript())
            set_scheme(args.scheme, "dark")
            with open(dark_filepath, "w") as f:
                if filetype == "latex":
                    f.write(get_scheme().to_latex())
                elif filetype == "css":
                    f.write(get_scheme().to_css())
                elif filetype == "js":
                    f.write(get_scheme().to_javascript())
        else:
            set_scheme(args.scheme, args.variant)
            with open(filepath, "w") as f:
                if filetype == "latex":
                    f.write(get_scheme().to_latex())
                elif filetype == "css":
                    f.write(get_scheme().to_css())
                elif filetype == "js":
                    f.write(get_scheme().to_javascript())
    elif args.command == "list":
        # sort available schemes alphabetically
        available.sort()
        pattern = args.pattern.replace("*", ".*").replace("?", ".")
        matches = [s for s in available if re.fullmatch(pattern, s)]
        if len(matches) == 0:
            print(f"No schemes match pattern `{args.pattern}`")
            quit(1)
        from rich.table import Table
        from rich.text import Text
        from rich.style import Style
        table = Table(show_lines = True)
        table.add_column("Name", justify="center")
        table.add_column("Sample", justify="center")
        for scheme in matches:
            set_scheme(scheme)
            table.add_row(
                Text(scheme, style = f"bold {get_scheme().foreground} on {get_scheme().background}"),
                get_scheme().to_rich_swatch()
            )
        console = Console()
        console.print(table)

        
