import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.text import Text

import pygmentation as pyg
from pygmentation.colors.models import *

USE_RELATIVE = False

SWATCH_INDEX = 0
TERMINAL_INDEX = 0
GRADIENT_INDEX = 0

IMAGE_DIR = Path(".swatches")
BRANCH = "main"
URL_BASE = f"https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/{BRANCH}/"

swatch_template = """<svg xmlns="http://www.w3.org/2000/svg" width="80" height="20" viewBox="0 0 80 20"><rect width="80" height="20" rx = "5" ry = "5" fill="{background}" /><text x="50%" y="50%" dy=".3em" fill="{text}" text-anchor="middle" font-family="monospace" font-size="11">{background}</text></svg>"""
comparison_swatch_template = """<svg xmlns="http://www.w3.org/2000/svg" width="80" height="20" viewBox="0 0 80 20"><defs><clipPath id="clip"><rect width="80" height="20" rx="5" ry="5"/></clipPath></defs><g clip-path="url(#clip)"><rect width="40" height="20" fill="{left}"/><rect width="40" height="20" x="40" fill="{right}"/></g></svg>"""
def swatch(background: str | pyg.Color, foreground: str | pyg.Color = "#000000"):
    global SWATCH_INDEX
    if not isinstance(background, pyg.Color):
        background = pyg.Color(background)
    if not isinstance(foreground, pyg.Color):
        foreground = pyg.Color(foreground)
    SWATCH_INDEX += 1
    svg = swatch_template.format(background = background, text = foreground)
    svg_file = IMAGE_DIR / f"swatch_{SWATCH_INDEX}.svg"
    with open(svg_file, "w") as f:
        f.write(svg)
    if USE_RELATIVE:
        url = ""
    else:
        url = URL_BASE
    url += str(svg_file)
    return md.image(url = url, description = background.css)

def comparison_swatch(left: str | ColorModel | pyg.Color, right: str | ColorModel | pyg.Color):
    global SWATCH_INDEX
    if not isinstance(left, pyg.Color):
        left = pyg.Color(left)
    if not isinstance(right, pyg.Color):
        right = pyg.Color(right)
    SWATCH_INDEX += 1
    svg = comparison_swatch_template.format(left = left, right = right)
    svg_file = IMAGE_DIR / f"swatch_{SWATCH_INDEX}.svg"
    with open(svg_file, "w") as f:
        f.write(svg)
    if USE_RELATIVE:
        url = ""
    else:
        url = URL_BASE
    url += str(svg_file)
    return md.image(url = url, description = f"Comparison of {left.css} and {right.css}")


def capture_terminal(command: str, columns: int = 88):
    global TERMINAL_INDEX
    TERMINAL_INDEX += 1
    svg_file = IMAGE_DIR / f"terminal_{TERMINAL_INDEX}.svg"
    svg_file.parent.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    venv_bin = str(Path(sys.executable).parent)
    env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
    src_dir = str(Path(__file__).parent / "src")
    env["PYTHONPATH"] = f"{src_dir}:{env.get('PYTHONPATH', '')}" if "PYTHONPATH" in env else src_dir
    env["COLUMNS"] = str(columns)
    env["LINES"] = "24"
    env["FORCE_COLOR"] = "1"
    env["TERM"] = "xterm-256color"

    bash_path = shutil.which("bash") or "/bin/bash"
    result = subprocess.run(
        command,
        shell=True,
        executable=bash_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    console = Console(record=True, width=columns, file=io.StringIO())
    console.print(Text.from_ansi(result.stdout), end="")
    console.save_svg(str(svg_file), title=command)

    if USE_RELATIVE:
        url = ""
    else:
        url = URL_BASE
    url += str(svg_file)
    return md.image(url=url, description=command)


