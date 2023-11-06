from .color_scheme import ColorScheme, Color, ColorFamily, SchemeType, EnumEx
import json
from pathlib import Path
from .scheme import schemes_json as schemes_json

import sys



# this is a pointer to the module object instance itself.
# this = sys.modules[__name__]


class DocType(EnumEx):
    REPORT = 1
    PRESENTATION = 2

# this.Scheme = None
# this.schemes_json = Path(__file__).parent / "color_schemes.json"
Scheme = None
schemes_json = Path(__file__).parent / "color_schemes.json"
with open(schemes_json, "r") as f:
    all_schemes = json.load(f)

def get_available_schemes():
    # returns a list of the names of all available schemes
    return list(all_schemes.keys())

def set_scheme(scheme: str = "twilight", scheme_type: str | SchemeType = "light"):
    global Scheme, schemes_json, all_schemes
    # this = sys.modules[__name__]

    if isinstance(scheme_type, str):
        scheme_type = SchemeType[scheme_type.upper()]
    
    if not scheme in all_schemes:
        raise ValueError(f"Scheme {scheme} not found")
    scheme_dict = all_schemes[scheme]
    if scheme_type.name.lower() in scheme_dict:
        scheme_dict = scheme_dict[scheme_type.name.lower()]
    else:
        # make sure that foreground and background lightnesses are appropriate for the scheme_type
        if scheme_type == SchemeType.LIGHT:
            # foreground should be dark, background should be light
            if Color(scheme_dict["foreground"]).is_lighter_than(Color(scheme_dict["background"])):
                scheme_dict["foreground"], scheme_dict["background"] = scheme_dict["background"], scheme_dict["foreground"]
        elif scheme_type == SchemeType.DARK:
            # foreground should be light, background should be dark
            if Color(scheme_dict["foreground"]).is_darker_than(Color(scheme_dict["background"])):
                scheme_dict["foreground"], scheme_dict["background"] = scheme_dict["background"], scheme_dict["foreground"]
    # this.Scheme = ColorScheme(
    Scheme = ColorScheme(
        scheme_dict,
        scheme_type
    )

def init(scheme: str = "twilight", scheme_type: str | SchemeType = "light", doc_type: str | DocType = "report"):


    from cycler import cycler
    import matplotlib.pyplot as plt
    

    if isinstance(doc_type, str):
        doc_type = DocType[doc_type.upper()]

    set_scheme(scheme, scheme_type)

    # Get a matplotlib cycler object for the color scheme, from Scheme.distinct[:].base, then Scheme.distinct[:].lightest, then Scheme.distinct[:].darkest
    # color_cycler = cycler(color = 
    #     [c.base.css for c in this.Scheme.distinct] +
    #     [c.base.css for c in this.Scheme.distinct] +
    #     [c.base.css for c in this.Scheme.distinct],
    #     linestyle = ["-"] * len(this.Scheme.distinct) + ["--"] * len(this.Scheme.distinct) + [":"] * len(this.Scheme.distinct)
    # )

    color_cycler = cycler(color =
        [c.base.css for c in Scheme.distinct] +
        [c.base.css for c in Scheme.distinct] +
        [c.base.css for c in Scheme.distinct],
        linestyle = ["-"] * len(Scheme.distinct) + ["--"] * len(Scheme.distinct) + [":"] * len(Scheme.distinct)
    )
    """
    Always:
        - Use Scheme.foreground for text
        - Use LaTeX interpreter, not matplotlib defualt
        - Computer Modern font
        - Use Scheme.background for axes facecolor
        - Use Scheme.background._5 for legend facecolor
        - Use color_cycler for line colors
        - Use Scheme.foreground for legend border
        - Rounded corners on legend border
        - Legend background opacity 0.5
    doc_type.REPORT:
        - Use Scheme.foreground for axes etc
        - Have top and right spines visible
        - Transparent figure facecolor
        - Report-appropriate aspect ratio 
    doc_type.PRESENTATION:
        - Have top and right spines invisible
        - Use Scheme.background for figure facecolor
        - Use Scheme.distinct[0] for axes etc
        - Use Scheme.distinct[0] for axis labels and ticks
        - Wider aspect ratio 
    """

    # # Set matplotlib rcParams
    # plt.rcParams.update({
    #     "text.usetex": True,
    #     "font.family": "serif",
    #     "font.serif": "Computer Modern Roman",
    #     "text.color": this.Scheme.foreground.css,
    #     "font.size": 12 if doc_type == DocType.REPORT else 16,
    #     "figure.facecolor": this.Scheme.background.base.css if doc_type == DocType.PRESENTATION else "none",
    #     "axes.facecolor": this.Scheme.background.base.css,
    #     "legend.facecolor": this.Scheme.background._5.css,
    #     "legend.edgecolor": this.Scheme.foreground.css,
    #     "legend.framealpha": 0.5,
    #     "legend.fancybox": True,
    #     "axes.prop_cycle": color_cycler,
    #     "axes.edgecolor": this.Scheme.foreground.css if doc_type == DocType.REPORT else this.Scheme.distinct[0].css,
    #     "axes.labelcolor": this.Scheme.foreground.css if doc_type == DocType.REPORT else this.Scheme.distinct[0].css,
    #     "axes.spines.top": True if doc_type == DocType.REPORT else False,
    #     "axes.spines.right": True if doc_type == DocType.REPORT else False,
    #     "xtick.color": this.Scheme.foreground.css if doc_type == DocType.REPORT else this.Scheme.distinct[0].css,
    #     "ytick.color": this.Scheme.foreground.css if doc_type == DocType.REPORT else this.Scheme.distinct[0].css,
    #     "figure.figsize": (6.4, 4.8) if doc_type == DocType.REPORT else (8, 4.5),
    #     "figure.dpi": 300,
    #     # "figure.constrained_layout.use": True,
    #     # "figure.constrained_layout.h_pad": 0.1,
    #     # "figure.constrained_layout.w_pad": 0.1,
    #     # "figure.constrained_layout.hspace": 0.1,
    #     # "figure.constrained_layout.wspace": 0.1,
    #     # "figure.constrained_layout.pad": 0.1
    # })

    # Set matplotlib rcParams
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": "Computer Modern Roman",
        "text.color": Scheme.foreground.css,
        "font.size": 12 if doc_type == DocType.REPORT else 16,
        "figure.facecolor": Scheme.background.base.css if doc_type == DocType.PRESENTATION else "none",
        "axes.facecolor": Scheme.background.base.css,
        "legend.facecolor": Scheme.background._5.css,
        "legend.edgecolor": Scheme.foreground.css,
        "legend.framealpha": 0.5,
        "legend.fancybox": True,
        "axes.prop_cycle": color_cycler,
        "axes.edgecolor": Scheme.foreground.css if doc_type == DocType.REPORT else Scheme.distinct[0].css,
        "axes.labelcolor": Scheme.foreground.css if doc_type == DocType.REPORT else Scheme.distinct[0].css,
        "axes.spines.top": True if doc_type == DocType.REPORT else False,
        "axes.spines.right": True if doc_type == DocType.REPORT else False,
        "xtick.color": Scheme.foreground.css if doc_type == DocType.REPORT else Scheme.distinct[0].css,
        "ytick.color": Scheme.foreground.css if doc_type == DocType.REPORT else Scheme.distinct[0].css,
        "figure.figsize": (6.4, 4.8) if doc_type == DocType.REPORT else (8, 4.5),
        "figure.dpi": 300,
        # "figure.constrained_layout.use": True,
        # "figure.constrained_layout.h_pad": 0.1,
        # "figure.constrained_layout.w_pad": 0.1,
        # "figure.constrained_layout.hspace": 0.1,
        # "figure.constrained_layout.wspace": 0.1,
        # "figure.constrained_layout.pad": 0.1
    })


def get_scheme() -> ColorScheme:
    return Scheme

def _set_color(rgb, g = None, b = None):
    ansi_escape = "\x1b["
    if g is None and b is None:
        r, g, b = rgb
    else:
        r = rgb
    return ansi_escape + "38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

def _set_background(rgb, g = None, b = None):
    ansi_escape = "\x1b["
    if g is None and b is None:
        r, g, b = rgb
    else:
        r = rgb
    return ansi_escape + "48;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

def _reset_color():
    ansi_escape = "\x1b["
    return ansi_escape + "0m"


def _get_preset(scheme, color):
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
        if eval(f"scheme.{p}.base") == color.base:
            return p
    return None




def square(col, variant = None):
    from rich.text import Text
    from rich.style import Style
    from rich.color import Color as RichColor
    if variant is None:
        c = col.base.rgb 
    else:
        c = col[variant].rgb
    return Text("█████\n█████", style=Style(color = RichColor.from_rgb(*c)))



def show_scheme(scheme = None, name = None, save = False, filepath = None):
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.console import Console
    from rich.style import Style
    from rich.color import Color as RichColor
    from rich import box
    if name is None:
        name = "Colour Scheme"
    if scheme is None:
        scheme = Scheme
    console = Console(record = save)
    width = console.size.width
    if width >= 112:
        show_scheme_wide(scheme, name, save, filepath)
        return
    def add_row(name, colour, alias = None):
        col1 = Text().append(name + ":\n", style = Style(color = RichColor.from_rgb(*scheme.foreground.base.rgb)))
        if alias is not None:
            col1.append(f"({alias.capitalize()})", style=Style(color = RichColor.from_rgb(*scheme.accents[0].base.rgb)))
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
    
    def add_empty_row():
        table.add_row(*["" for _ in range(8)])

    table = Table(show_header = False, box=box.SIMPLE, leading = 1, padding = 0)
    table.add_column("Name", justify="right")
    table.add_column("Base", justify="center")
    table.add_column("", justify="center")
    table.add_column("1", justify="center")
    table.add_column("2", justify="center")
    table.add_column("3", justify="center")
    table.add_column("4", justify="center")
    table.add_column("5", justify="center")

    add_row("Foreground", scheme.foreground)
    add_row("Background", scheme.background)
    add_empty_row()
    for i, col in enumerate(scheme.accents):
        alias = _get_preset(scheme, col)
        add_row(f"Accent {i+1}", col, alias = alias)
    if len(scheme.surfaces) > 0:
        add_empty_row()
        for i, col in enumerate(scheme.surfaces):
            add_row(f"Surface {i+1}", col)
    
    panel = Panel.fit(table, title = name, style = Style(bgcolor = RichColor.from_rgb(*scheme.background.base.rgb), color = RichColor.from_rgb(*scheme.foreground.base.rgb)))
    console.print(panel)
    if save:
        if filepath is None:
            filepath = Path(f"{name}.svg".replace(" ", "_"))
        
        console.save_svg(filepath)


def show_scheme_wide(scheme = None, name = None, save = False, filepath = None):
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.console import Console
    from rich.style import Style
    from rich.color import Color as RichColor
    from rich import box
    if name is None:
        name = "Colour Scheme"
    if scheme is None:
        scheme = Scheme
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
    
    def add_empty_row():
        table.add_row(
            *["" for i in range(17)]
        )

    foreground_style = Style(color = RichColor.from_rgb(*scheme.foreground.base.rgb))
    accent_style = Style(color = RichColor.from_rgb(*scheme.accents[0].base.rgb))

    table = Table(show_header = True, box=box.SIMPLE, leading = 1, padding = 0)

    table.add_column("Name", justify="right")
    table.add_column("Base", justify="center")
    table.add_column("", justify="center")
    table.add_column("1", justify="center")
    table.add_column("2", justify="center")
    table.add_column("3", justify="center")
    table.add_column("4", justify="center")
    table.add_column("5", justify="center")
    table.add_column("", justify="center")
    table.add_column("Name", justify="right")
    table.add_column("Base", justify="center")
    table.add_column("", justify="center")
    table.add_column("1", justify="center")
    table.add_column("2", justify="center")
    table.add_column("3", justify="center")
    table.add_column("4", justify="center")
    table.add_column("5", justify="center")

    add_row({"name": "Foreground", "colour": scheme.foreground, "alias": None}, {"name": "Background", "colour": scheme.background, "alias": None})
    add_empty_row()
    for i in range(0, len(scheme.accents), 2):
        l_alias = _get_preset(scheme, scheme.accents[i])
        left = {"name": f"Accent {i+1}", "colour": scheme.accents[i], "alias": l_alias}
        if i+1 < len(scheme.accents):
            r_alias = _get_preset(scheme, scheme.accents[i+1])
            right = {"name": f"Accent {i+2}", "colour": scheme.accents[i+1], "alias": r_alias}
        else:
            right = None
        add_row(left, right)
    
    if len(scheme.surfaces) > 0:
        add_empty_row()
        for i in range(0, len(scheme.surfaces), 2):
            left = {"name": f"Surface {i+1}", "colour": scheme.surfaces[i], "alias": None}
            if i+1 < len(scheme.surfaces):
                right = {"name": f"Surface {i+2}", "colour": scheme.surfaces[i+1], "alias": None}
            else:
                right = None
            add_row(left, right)
    
    console = Console(record = save)
    panel = Panel.fit(table, title = name, style = Style(bgcolor = RichColor.from_rgb(*scheme.background.base.rgb), color = RichColor.from_rgb(*scheme.foreground.base.rgb)), padding = (1,2))
    console.print(panel)
    if save:
        if filepath is None:
            filepath = Path(f"{name}.svg".replace(" ", "_"))
        
        console.save_svg(filepath)

