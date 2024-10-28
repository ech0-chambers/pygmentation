import argparse
from pathlib import Path
from rich.console import Console
from rich.prompt import IntPrompt
from .pygmentation import show_scheme, set_scheme, get_scheme, get_available_schemes, handle_unknown_scheme, show, save, write, list_schemes

def parse_args():
    # pygmentation show [--show-codes|-s] [--code-type-c <hex|rgb|hsl|hsv|Lab>] <scheme> [variant] -- Show a scheme in the terminal, optionally only showing the light or dark variant (default: both)
    # pygmentation save -f <filename> <scheme> [variant] -- Save a .svg file of a scheme, optionally only saving the light or dark variant (default: both)
    # pygmentation write -f <filename> -t <latex|css> <scheme> [variant] -- Write a .tex or .css file of a scheme, optionally only saving the light or dark variant (default: both). -t is optional, inferred from filename extension if not provided.
    # pygmentation list --names-only <pattern> [variant] -- List all available schemes, with a sample of each. If pattern is provided, only schemes matching the pattern are listed (accepts standard shell wildcards). If --names-nly, just prints the names with no sample

    parser = argparse.ArgumentParser(prog = "pygmentation", description = "A command-line tool for generating color schemes for quantum optics plots.")
    subparsers = parser.add_subparsers(dest = "command", required = True)

    show_parser = subparsers.add_parser("show", help = "Show a scheme in the terminal, optionally only showing the light or dark variant (default: both)")
    show_parser.add_argument("scheme", help = "The name of the scheme to show")
    show_parser.add_argument("variant", nargs = "?", default = "both", choices = ["both", "light", "dark"], help = "The variant of the scheme to show (default: both)")
    show_parser.add_argument("-s", "--show-codes", action = "store_true", help = "Show the color codes for the scheme")
    show_parser.add_argument("-c", "--code-type", choices = ["hex", "rgb", "hsl", "hsv", "Lab"], help = "The type of color codes to show (default: hex)")

    save_parser = subparsers.add_parser("save", help = "Save a .svg file of a scheme, optionally only saving the light or dark variant (default: both)")
    save_parser.add_argument("-f", "--filename", required = True, help = "The name of the file to save")
    save_parser.add_argument("scheme", help = "The name of the scheme to save")
    save_parser.add_argument("variant", nargs = "?", default = "both", choices = ["both", "light", "dark"], help = "The variant of the scheme to save (default: both)")

    write_parser = subparsers.add_parser("write", help = "Write a .tex, .css, .tcss (textual css), or .js file of a scheme, optionally only saving the light or dark variant (default: both)")
    write_parser.add_argument("-f", "--filename", required = True, help = "The name of the file to save")
    write_parser.add_argument("-t", "--type", choices = ["latex", "css", "tcss", "js"], help = "The type of file to write (default: inferred from filename extension)")
    write_parser.add_argument("scheme", help = "The name of the scheme to write")
    write_parser.add_argument("variant", nargs = "?", default = "both", choices = ["both", "light", "dark"], help = "The variant of the scheme to write (default: both)")

    list_parser = subparsers.add_parser("list", help = "List all available schemes, with a sample of each. If pattern is provided, only schemes matching the pattern are listed (accepts standard shell wildcards)")
    list_parser.add_argument("--names-only", action = "store_true", help = "Just print the names of the schemes with no sample")
    list_parser.add_argument("pattern", nargs = "?", default = "*", help = "A pattern to match against scheme names (default: *)")
    list_parser.add_argument("variant", nargs = "?", default = "light", choices = ["light", "dark"], help = "The variant of the schemes to list (default: light)")

    return parser.parse_args()


def main():

    args = parse_args()
    available = get_available_schemes()

    if args.command != "list" and args.scheme not in available:
        args.scheme = handle_unknown_scheme(args.scheme)

    if args.command == "show":
        show(args.scheme, args.variant, args.show_codes, args.code_type)
        return
    
    if args.command == "save":
        save(args.filename, args.scheme, args.variant)
        return
        
    if args.command == "write":
        filepath = Path(args.filename)
        format_map = {
            ".tex": "latex",
            ".css": "css",
            ".less": "less",
            ".tcss": "tcss",
            ".js": "js"
        }
        if args.type is not None:
            filetype = args.type
        elif filepath.suffix in format_map:
            filetype = format_map[filepath.suffix]
        else:
            raise ValueError(f"Filename must have {', '.join(list(format_map.keys())[:-1])}, or {list(format_map.keys())[-1]} extension, or type must be specified with -t/--type")
        write(args.filename, args.scheme, args.variant, filetype)
        
    elif args.command == "list":
        # sort available schemes alphabetically
        available.sort()
        names_only = args.names_only
        pattern = args.pattern
        if pattern.startswith("re:"):
            pattern = pattern[3:]
        else:
            pattern = pattern.replace("*", ".*").replace("?", ".")
        list_schemes(names_only, pattern, available, True, args.variant.lower() == "dark")

if __name__ == "__main__":
    main()
