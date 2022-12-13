from .color_scheme import ColorScheme, Color, ColorFamily, SchemeType, EnumEx
import json
from pathlib import Path
from cycler import cycler
import matplotlib.pyplot as plt
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

def init(scheme: str = "twilight", scheme_type: str | SchemeType = "light", doc_type: str | DocType = "report"):
    global Scheme, schemes_json
    # this = sys.modules[__name__]
    
    with open(schemes_json, "r") as f:
        all_schemes = json.load(f)
    
    if isinstance(scheme_type, str):
        scheme_type = SchemeType[scheme_type.upper()]
    if isinstance(doc_type, str):
        doc_type = DocType[doc_type.upper()]
    
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
        scheme_dict["colors"],
        scheme_dict["foreground"],
        scheme_dict["background"],
        scheme_type
    )

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