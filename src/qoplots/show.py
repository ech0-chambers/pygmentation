from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.style import Style
from rich.color import Color
from rich import print as rprint
from rich import box


def square(col, variant = None):
    if variant is None:
        c = col.base.rgb 
    else:
        c = col[variant].rgb
    return Text("████\n████", style=Style(color = Color.from_rgb(*c)))



def show_scheme(scheme, name = None):
    if name is None:
        name = "Colour Scheme"
    console = Console()
    width = console.size.width
    if width > 100:
        show_scheme_wide(scheme)
        return
    def add_row(name, colour, alias = None):
        col1 = Text().append(name + ":\n", style = Style(color = Color.from_rgb(*scheme.foreground.base.rgb)))
        if alias is not None:
            col1.append(f"({alias.capitalize()})", style=Style(color = Color.from_rgb(*scheme.accents[0].base.rgb)))
        table.add_row(
            col1,
            square(colour),
            "  ",
            square(colour, 1),
            square(colour, 2),
            square(colour, 3),
            square(colour, 4),
            square(colour, 5)
        )
    table = Table(show_header = False, box=box.SIMPLE, leading = 1, padding = 0)
    table.add_column("name", justify="right")
    table.add_column("base", justify="center")
    table.add_column("space", justify="center")
    table.add_column("1", justify="center")
    table.add_column("2", justify="center")
    table.add_column("3", justify="center")
    table.add_column("4", justify="center")
    table.add_column("5", justify="center")

    add_row("Foreground", scheme.foreground)
    add_row("Background", scheme.background)
    for i, col in enumerate(scheme.accents):
        alias = _get_preset(scheme, col)
        add_row(f"Accent {i+1}", col, alias = alias)
    for i, col in enumerate(scheme.surfaces):
        add_row(f"Surface {i+1}", col)
    
    panel = Panel(table, title = name, style = Style(bgcolor = Color.from_rgb(*scheme.background.base.rgb), color = Color.from_rgb(*scheme.background.base.rgb)))
    console.print(panel)


def show_scheme_wide(scheme, name = None):
    if name is None:
        name = "Colour Scheme"
    def add_row(left, right = None):

        l_name = Text().append(f'{left["name"]}:\n', style = foreground_style)
        if left["alias"] is not None:
            l_name.append(f"({left['alias'].capitalize()})", style=accent_style)
        if right is None:
            table.add_row(
                l_name,
                square(left["colour"]),
                "  ",
                square(left["colour"], 1),
                square(left["colour"], 2),
                square(left["colour"], 3),
                square(left["colour"], 4),
                square(left["colour"], 5),
                "  ",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                ""
            )
            return
        r_name = Text().append(f'{right["name"]}:\n', style = foreground_style)
        if right["alias"] is not None:
            r_name.append(f"({right['alias'].capitalize()})", style=accent_style)
        
        table.add_row(
            l_name,
            square(left["colour"]),
            "  ",
            square(left["colour"], 1),
            square(left["colour"], 2),
            square(left["colour"], 3),
            square(left["colour"], 4),
            square(left["colour"], 5),
            "  ",
            r_name,
            square(right["colour"]),
            "  ",
            square(right["colour"], 1),
            square(right["colour"], 2),
            square(right["colour"], 3),
            square(right["colour"], 4),
            square(right["colour"], 5)
        )

    foreground_style = Style(color = Color.from_rgb(*scheme.foreground.base.rgb))
    accent_style = Style(color = Color.from_rgb(*scheme.accents[0].base.rgb))

    table = Table(show_header = False, box=box.SIMPLE, leading = 1, padding = 0)

    table.add_column("name_l", justify="right")
    table.add_column("base_l", justify="center")
    table.add_column("space_l", justify="center")
    table.add_column("1_l", justify="center")
    table.add_column("2_l", justify="center")
    table.add_column("3_l", justify="center")
    table.add_column("4_l", justify="center")
    table.add_column("5_l", justify="center")
    table.add_column("space", justify="center")
    table.add_column("name_r", justify="right")
    table.add_column("base_r", justify="center")
    table.add_column("space_r", justify="center")
    table.add_column("1_r", justify="center")
    table.add_column("2_r", justify="center")
    table.add_column("3_r", justify="center")
    table.add_column("4_r", justify="center")
    table.add_column("5_r", justify="center")

    add_row({"name": "Foreground", "colour": scheme.foreground, "alias": None}, {"name": "Background", "colour": scheme.background, "alias": None})
    for i in range(0, len(scheme.accents), 2):
        l_alias = _get_preset(scheme, scheme.accents[i])
        left = {"name": f"Accent {i+1}", "colour": scheme.accents[i], "alias": l_alias}
        if i+1 < len(scheme.accents):
            r_alias = _get_preset(scheme, scheme.accents[i+1])
            right = {"name": f"Accent {i+2}", "colour": scheme.accents[i+1], "alias": r_alias}
        else:
            right = None
        add_row(left, right)

    for i in range(0, len(scheme.surfaces), 2):
        left = {"name": f"Surface {i+1}", "colour": scheme.surfaces[i], "alias": None}
        if i+1 < len(scheme.surfaces):
            right = {"name": f"Surface {i+2}", "colour": scheme.surfaces[i+1], "alias": None}
        else:
            right = None
        add_row(left, right)
    
    console = Console()
    panel = Panel(table, title = name, style = Style(bgcolor = Color.from_rgb(*scheme.background.base.rgb), color = Color.from_rgb(*scheme.background.base.rgb)))
    console.print(panel)