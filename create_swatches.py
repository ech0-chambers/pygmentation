import re
from pathlib import Path

pre_file = Path("pre_README.md")
post_file = Path("README.md")

if not pre_file.exists():
    print("No pre file found.")
    exit(1)

if post_file.exists():
    post_file.unlink()


# Read in the pre file
with open(pre_file, "r") as f:
    contents = f.read()

# find anything matching swatch(#aaaaaa) or swatch(#aaaaaa, #bbbbbb)
swatch_re = re.compile(r"swatch\((?P<background>#[0-9a-fA-F]{6})(?:,\s*?(?P<text>#[0-9a-fA-F]{6}))?\)")

# replace with appropriate svg

svg_template = """<svg xmlns="http://www.w3.org/2000/svg" width="80" height="20" viewBox="0 0 80 20"><rect width="80" height="20" rx = "5" ry = "5" fill="{background}" /><text x="50%" y="50%" dy=".3em" fill="{text}" text-anchor="middle" font-family="monospace" font-size="11">{background}</text></svg>"""

with open(post_file, "w") as f:
    for match in swatch_re.finditer(contents):
        background = match.group("background")
        text = match.group("text") or "#000000"
        svg = svg_template.format(background=background, text=text)
        contents = contents.replace(match.group(0), svg)
    f.write(contents)
