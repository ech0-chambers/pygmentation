import html
import math
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ._fonts import FIRA_CODE_WOFF2_BASE64
from .colors.color import Color
from .colors.scheme import ColorFamily, ColorScheme

# Formatter mappings for color code representations (e.g. hex, rgb, hsl, hsv, lab, oklab, oklch)
CODE_FORMATTERS: dict[str, Callable[[Color], str]] = {
    "hex": lambda c: f"#{c.hex}",
    "rgb": lambda c: f"{c.as_255.r}, {c.as_255.g}, {c.as_255.b}",
    "hsl": lambda c: f"{c.h:.0f}°, {c.s * 100:.0f}%, {c.l * 100:.0f}%",
    "hsv": lambda c: f"{c.hsv.h:.0f}°, {c.hsv.s * 100:.0f}%, {c.hsv.v * 100:.0f}%",
    "lab": lambda c: f"{c.lab.l:.0f}, {c.lab.a:.0f}, {c.lab.b:.0f}",
    "xyz": lambda c: f"{c.xyz.x:.0f}, {c.xyz.y:.0f}, {c.xyz.z:.0f}",
    "oklab": lambda c: f"{c.oklab.l:.2f}, {c.oklab.a:.2f}, {c.oklab.b:.2f}",
    "oklch": lambda c: f"{c.oklch.l:.2f}, {c.oklch.c:.2f}, {c.oklch.h:.0f}°",
}


class Exporter(ABC):
    """
    Abstract base class for exporting colour schemes into external formats.

    Attributes
    ----------
    format_name : str
        The canonical name of the export format (e.g. 'css', 'latex').
    file_extensions : tuple[str, ...]
        Tuple of common file extensions associated with the export format (e.g.
        `('.css', 'css')`).
    """
    format_name: ClassVar[str]
    file_extensions: ClassVar[tuple[str, ...]]

    @staticmethod
    def canonical_name(root: str, index: int | None) -> str:
        """
        Generate the identifier name for a colour in this format.

        Parameters
        ----------
        root : str
            Base category name for the colour (e.g. 'foreground', 'accent').
        index : int | None
            Optional 0-based variant or accent index. If `None`, the root name
            is returned without an index suffix.

        Returns
        -------
        str
            The formatted identifier name.
        """
        if index is None:
            return root
        return f"{root}{index}"

    @staticmethod
    def canonical_alias_name(root: str) -> str:
        """
        Generate the identifier name for a semantic colour alias.

        Parameters
        ----------
        root : str
            The semantic alias name (e.g. 'error', 'red').

        Returns
        -------
        str
            The formatted alias identifier name.
        """
        return root

    @abstractmethod
    def format_color(self, color: Color, name: str) -> str:
        """
        Format a single colour definition in the target syntax.

        Parameters
        ----------
        color : Color
            The colour to format.
        name : str
            The identifier name for the colour.

        Returns
        -------
        str
            The formatted colour definition string.
        """
        pass

    @abstractmethod
    def format_alias(self, name: str, target: str) -> str:
        """
        Format a semantic alias pointing to another colour identifier.

        Parameters
        ----------
        name : str
            The alias identifier name.
        target : str
            The target colour identifier name being aliased.

        Returns
        -------
        str
            The formatted alias definition string.
        """
        pass

    @abstractmethod
    def format_alias_family(self, name: str, target: str) -> list[str]:
        """
        Format an alias family mapping an alias and its variants to a target.

        Parameters
        ----------
        name : str
            The alias family identifier name.
        target : str
            The target family identifier name.

        Returns
        -------
        list[str]
            List of formatted alias definition strings for the family.
        """
        pass

    @abstractmethod
    def format_family(self, family: ColorFamily, name: str) -> list[str]:
        """
        Format a colour family, including its base colour and variants.

        Parameters
        ----------
        family : ColorFamily
            The colour family to format.
        name : str
            The base identifier name for the family.

        Returns
        -------
        list[str]
            List of formatted colour definition strings for the family.
        """
        pass

    def export(self, scheme: ColorScheme) -> str:
        """
        Export an entire colour scheme to a string in the target format.

        Parameters
        ----------
        scheme : ColorScheme
            The colour scheme to export.

        Returns
        -------
        str
            The complete exported content as a string.
        """
        output = []

        output.extend(
            self.format_family(
                scheme.foreground, self.canonical_name("foreground", None)
            )
        )
        output.extend(
            self.format_family(
                scheme.background, self.canonical_name("background", None)
            )
        )
        for i, accent in enumerate(scheme.accents):
            output.extend(self.format_family(accent, self.canonical_name("accents", i)))

        for i, surface in enumerate(scheme.surfaces):
            output.extend(
                self.format_family(surface, self.canonical_name("surfaces", i))
            )

        output.extend(
            self.format_family(
                scheme.auto_surface, self.canonical_name("auto_surface", None)
            )
        )

        for alias_name, color in scheme.aliases.items():
            canonical = scheme.get_canonical_name(color)
            if canonical is not None:
                name, index = canonical
                output.extend(
                    self.format_alias_family(
                        self.canonical_alias_name(alias_name),
                        self.canonical_name(name, index),
                    )
                )

        for alias_name, color in [
            ("error", scheme.error),
            ("warning", scheme.warning),
            ("success", scheme.success),
            ("info", scheme.info),
        ]:
            canonical = scheme.get_canonical_name(color)
            if canonical is not None:
                name, index = canonical
                output.extend(
                    self.format_alias_family(
                        self.canonical_alias_name(alias_name),
                        self.canonical_name(name, index),
                    )
                )

        return "\n".join(output)

    def save(self, scheme: ColorScheme, filepath: Path | str) -> None:
        """
        Export a colour scheme and write the result to a file.

        Parameters
        ----------
        scheme : ColorScheme
            The colour scheme to export.
        filepath : Path | str
            Filepath where the exported output should be saved.
        """
        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        output = self.export(scheme)
        with open(filepath, "w+", encoding="utf-8") as file:
            file.write(output)


class LatexExporter(Exporter):
    """
    Export colour schemes to LaTeX `xcolor` commands (`\\definecolor`).

    Attributes
    ----------
    format_name : str
        Format identifier ('latex').
    file_extensions : tuple[str, ...]
        Associated file extensions (`'.tex'`, `'.sty'`, `'.cls'`).
    """
    format_name: ClassVar[str] = "latex"
    file_extensions: ClassVar[tuple[str, ...]] = (".tex", ".sty", ".cls")

    @staticmethod
    def canonical_name(root: str, index: int | None) -> str:
        root = "".join(r.capitalize() for r in root.split("_"))
        if root in ["Foreground", "Background"]:
            root += "Colour"
        if root.endswith("s"):
            root = root[:-1]
        if index is None:
            return root
        return f"{root}{index + 1}"

    @staticmethod
    def canonical_alias_name(root: str) -> str:
        return f"{root.capitalize()}"

    def format_color(self, color: Color, name: str) -> str:
        return rf"\definecolor{{{name}}}{{HTML}}{{{color.hex}}}"

    def format_family(self, family: ColorFamily, name: str) -> list[str]:
        out = []
        out.append(self.format_color(family.base, name))
        out.extend(
            self.format_color(v, name=f"{name}_{i + 1}")
            for i, v in enumerate(family.variants)
        )
        return out

    def format_alias(self, name: str, target: str) -> str:
        return rf"\colorlet{{{name}}}{{{target}}}"

    def format_alias_family(self, name: str, target: str) -> list[str]:
        out = []
        out.append(self.format_alias(name, target))
        for i in range(1, 6):
            out.append(self.format_alias(f"{name}_{i}", f"{target}_{i}"))
        return out


class CssExporter(Exporter):
    """
    Export colour schemes to CSS custom properties (`--clr-*`).

    Attributes
    ----------
    format_name : str
        Format identifier ('css').
    file_extensions : tuple[str, ...]
        Associated file extensions (`'.css'`, `'css'`).
    """
    format_name: ClassVar[str] = "css"
    file_extensions: ClassVar[tuple[str, ...]] = (".css", "css")

    @staticmethod
    def canonical_name(root: str, index: int | None) -> str:
        if root.endswith("s"):
            root = root[:-1]

        if index is None:
            return f"--clr-{root}"
        return f"--clr-{root}{index + 1}"

    @staticmethod
    def canonical_alias_name(root: str) -> str:
        return f"--clr-{root}"

    def format_color(self, color: Color, name: str) -> str:
        """
        Format a colour as CSS custom properties in both hex and RGB triplet.

        Defines both `{name}: #{hex};` and `{name}-rgb: {r}, {g}, {b};` so that
        colours can easily be used with CSS `rgb()` or `rgba()` functions.

        Parameters
        ----------
        color : Color
            The colour to format.
        name : str
            The CSS property name (e.g. '--clr-foreground').

        Returns
        -------
        str
            The CSS declarations for the colour.
        """
        c = color.as_255
        return f"{name}: #{color.hex};\n{name}-rgb: {c.r}, {c.g}, {c.b};"

    def format_family(self, family: ColorFamily, name: str) -> list[str]:
        out = []
        out.append(self.format_color(family.base, name))
        out.extend(
            self.format_color(v, name=f"{name}-{i + 1}")
            for i, v in enumerate(family.variants)
        )
        return out

    def format_alias(self, name: str, target: str) -> str:
        """
        Format a CSS property alias referencing another property via `var()`.

        Defines both `{name}: var({target});` and `{name}-rgb:
        var({target}-rgb);`.

        Parameters
        ----------
        name : str
            The alias CSS property name.
        target : str
            The target CSS property name being aliased.

        Returns
        -------
        str
            The CSS variable assignment declarations.
        """
        return f"{name}: var({target});\n{name}-rgb: var({target}-rgb);"

    def format_alias_family(self, name: str, target: str) -> list[str]:
        out = []
        out.append(self.format_alias(name, target))
        for i in range(1, 6):
            out.append(self.format_alias(f"{name}-{i}", f"{target}-{i}"))
        return out

    def export(self, scheme: ColorScheme) -> str:
        """
        Export the colour scheme as CSS custom properties in a `:root` block.

        Parameters
        ----------
        scheme : ColorScheme
            The colour scheme to export.

        Returns
        -------
        str
            The CSS custom properties wrapped inside `:root { ... }`.
        """
        out = super().export(scheme)
        return f":root{{\n{out}\n}}"


class LessExporter(Exporter):
    """
    Export colour schemes to Less variables (`@clr-*`).

    Attributes
    ----------
    format_name : str
        Format identifier ('less').
    file_extensions : tuple[str, ...]
        Associated file extensions (`'.less'`, `'less'`, `'less.js'`,
        `'.less.js'`).
    """
    format_name: ClassVar[str] = "less"
    file_extensions: ClassVar[tuple[str, ...]] = (
        ".less",
        "less",
        "less.js",
        ".less.js",
    )

    @staticmethod
    def canonical_name(root: str, index: int | None) -> str:
        if root.endswith("s"):
            root = root[:-1]

        if index is None:
            return f"@clr-{root}"
        return f"@clr-{root}{index + 1}"

    @staticmethod
    def canonical_alias_name(root: str) -> str:
        return f"@clr-{root}"

    def format_color(self, color: Color, name: str) -> str:
        return f"{name}: #{color.hex};"

    def format_family(self, family: ColorFamily, name: str) -> list[str]:
        out = []
        out.append(self.format_color(family.base, name))
        out.extend(
            self.format_color(v, name=f"{name}-{i + 1}")
            for i, v in enumerate(family.variants)
        )
        return out

    def format_alias(self, name: str, target: str) -> str:
        return f"{name}: {target};"

    def format_alias_family(self, name: str, target: str) -> list[str]:
        out = []
        out.append(self.format_alias(name, target))
        for i in range(1, 6):
            out.append(self.format_alias(f"{name}-{i}", f"{target}-{i}"))
        return out


class TextualExporter(Exporter):
    """
    Export colour schemes to Textual CSS variables (`$clr-*`).

    Attributes
    ----------
    format_name : str
        Format identifier ('textual').
    file_extensions : tuple[str, ...]
        Associated file extensions (`'.tcss'`, `'tcss'`).
    """
    format_name: ClassVar[str] = "textual"
    file_extensions: ClassVar[tuple[str, ...]] = (
        ".tcss",
        "tcss",
    )

    @staticmethod
    def canonical_name(root: str, index: int | None) -> str:
        if root.endswith("s"):
            root = root[:-1]

        if index is None:
            return f"$clr-{root}"
        return f"$clr-{root}{index + 1}"

    @staticmethod
    def canonical_alias_name(root: str) -> str:
        return f"$clr-{root}"

    def format_color(self, color: Color, name: str) -> str:
        return f"{name}: #{color.hex};"

    def format_family(self, family: ColorFamily, name: str) -> list[str]:
        out = []
        out.append(self.format_color(family.base, name))
        out.extend(
            self.format_color(v, name=f"{name}-{i + 1}")
            for i, v in enumerate(family.variants)
        )
        return out

    def format_alias(self, name: str, target: str) -> str:
        return f"{name}: {target};"

    def format_alias_family(self, name: str, target: str) -> list[str]:
        out = []
        out.append(self.format_alias(name, target))
        for i in range(1, 6):
            out.append(self.format_alias(f"{name}-{i}", f"{target}-{i}"))
        return out


class JavascriptExporter(Exporter):
    """
    Export colour schemes to a JavaScript object literal
    (`const colors = {...}`).

    Attributes
    ----------
    format_name : str
        Format identifier ('javascript').
    file_extensions : tuple[str, ...]
        Associated file extensions (`'.js'`, `'js'`).
    """
    format_name: ClassVar[str] = "javascript"
    file_extensions: ClassVar[tuple[str, ...]] = (".js", "js")

    @staticmethod
    def canonical_name(root: str, index: int | None) -> str:
        if index is None:
            return f"colors.{root}"
        return f"colors.{root}[{index}]"

    @staticmethod
    def canonical_alias_name(root: str) -> str:
        return f"colors.{root}"

    def format_color(self, color: Color, name: str = "") -> str:
        return f"#{color.hex}"

    def format_alias(self, name: str, target: str) -> str:
        return f"{name} = {target};"

    def format_alias_family(self, name: str, target: str) -> list[str]:
        return [self.format_alias(name, target)]

    def format_family(
        self, family: ColorFamily, name: str = "", indent: int = 2
    ) -> list[str]:
        """
        Format a colour family as a structured JavaScript object literal.

        Parameters
        ----------
        family : ColorFamily
            The colour family to format.
        name : str, optional
            Optional family name identifier.
        indent : int, optional
            Number of indentation spaces. Defaults to 2.

        Returns
        -------
        list[str]
            Lines of JavaScript object syntax representing the family with
            base, indexed keys (`0` to `5`), and a `variants` array.
        """
        pad = " " * indent
        lines = [f"{pad}{{"]
        lines.append(f'{pad}  base: "#{family.base.hex}",')
        lines.append(f'{pad}  0: "#{family.base.hex}",')
        for i, v in enumerate(family.variants):
            lines.append(f'{pad}  {i + 1}: "#{v.hex}",')
        lines.append(f"{pad}  variants: [")
        for v in family.variants:
            lines.append(f'{pad}    "#{v.hex}",')
        lines.append(f"{pad}  ],")
        lines.append(f"{pad}}}")
        return lines

    def export(self, scheme: ColorScheme) -> str:
        """
        Export the colour scheme as a JavaScript `const colors = { ... }`
        object.

        Parameters
        ----------
        scheme : ColorScheme
            The colour scheme to export.

        Returns
        -------
        str
            JavaScript module code defining the colour scheme object and alias
            assignments.
        """
        lines = ["const colors = {"]
        lines.append(
            f"  foreground: {self._format_family_block(scheme.foreground, 2)},"
        )
        lines.append(
            f"  background: {self._format_family_block(scheme.background, 2)},"
        )

        lines.append("  accents: [")
        for accent in scheme.accents:
            lines.append(f"{self._format_family_block(accent, 4)},")
        lines.append("  ],")

        lines.append("  surfaces: [")
        if scheme.surfaces:
            for surface in scheme.surfaces:
                lines.append(f"{self._format_family_block(surface, 4)},")
        lines.append("  ],")

        if scheme.auto_surface is not None:
            lines.append(
                f"  auto_surface: {self._format_family_block(scheme.auto_surface, 2)},"
            )
        else:
            lines.append("  auto_surface: null,")

        lines.append("};")
        lines.append("")

        for alias_name, color in scheme.aliases.items():
            canonical = scheme.get_canonical_name(color)
            if canonical is not None:
                name, idx = canonical
                target = self.canonical_name(name, idx)
                alias = self.canonical_alias_name(alias_name)
                lines.append(self.format_alias(alias, target))

        for alias_name in ["error", "warning", "success", "info"]:
            color = getattr(scheme, alias_name)
            canonical = scheme.get_canonical_name(color)
            if canonical is not None:
                name, idx = canonical
                target = self.canonical_name(name, idx)
                alias = self.canonical_alias_name(alias_name)
                lines.append(self.format_alias(alias, target))

        return "\n".join(lines)

    def _format_family_block(self, family: ColorFamily, indent: int) -> str:
        lines = self.format_family(family, indent=indent)
        if indent == 2:
            return "\n".join(lines).lstrip()
        return "\n".join(lines)


@dataclass(frozen=True)
class _SvgLayout:
    # Dimensions and coordinates for rendering an SVG palette
    base_swatch_width: int
    variant_swatch_width: int
    swatch_height: int
    swatch_corner_radius: int
    label_width: int
    total_width: int
    left_column_x: int
    right_column_x: int
    swatch_offsets: list[int]
    swatch_widths: list[int]
    pad_x: int = 24
    pad_y: int = 20
    column_gap: int = 32
    row_gap: int = 18
    separator_gap: int = 36
    line_height: int = 17
    alias_line_height: int = 15
    char_width: float = 7.8
    code_font_size: int = 10
    code_char_width: float = 6.2
    font_size: int = 13
    header_font_size: int = 11

    @property
    def swatch_width(self) -> int:
        return self.variant_swatch_width


class SvgExporter(Exporter):
    """
    Export colour schemes to standalone visual SVG palette diagrams.

    Parameters
    ----------
    title : str | None, optional
        Optional title displayed in the SVG header. Defaults to the scheme
        name.
    code_type : str | None, optional
        Format of colour codes displayed beneath swatches (e.g. 'hex', 'rgb',
        'hsl', 'oklch'). If `None`, colour codes are omitted.
    dist_threshold : float, optional
        If a swatch is too similar to the background colour to be visually
        distinguishable, it is given a subtle border. This is the threshold
        Euclidean distance in Oklab space at which this occurs.
    base_aspect_ratio : float, optional
        Aspect ratio (width / height) for base colour swatches. Defaults to
        2.0.
    variant_aspect_ratio : float, optional
        Aspect ratio (width / height) for variant swatches. Defaults to
        1.0.
    swatch_height : int, optional
        Height of colour swatches in pixels. Defaults to 33.
    embed_font : bool, optional
        Whether to embed the base64-encoded WOFF2 font directly in the SVG
        `<style>` block. If `False`, the font definition is omitted and only
        `font-family` rules are emitted. Defaults to `True`.

    Attributes
    ----------
    format_name : str
        Format identifier ('svg').
    file_extensions : tuple[str, ...]
        Associated file extensions (`'.svg'`, `'svg'`).
    title : str | None
        Title displayed in the SVG header.
    code_type : str | None
        Colour code format displayed beneath swatches.
    dist_threshold : float
        Distance threshold for swatch borders.
    base_aspect_ratio : float
        Aspect ratio for base colour swatches.
    variant_aspect_ratio : float
        Aspect ratio for variant colour swatches.
    swatch_height : int
        Height of swatches in pixels.
    embed_font : bool
        Whether the font subset is embedded in the SVG.
    """

    format_name: ClassVar[str] = "svg"
    file_extensions: ClassVar[tuple[str, ...]] = (".svg", "svg")

    def __init__(
        self,
        title: str | None = None,
        code_type: str | None = None,
        dist_threshold: float = 5.0,
        base_aspect_ratio: float = 2.0,
        variant_aspect_ratio: float = 1.0,
        swatch_height: int = 33,
        embed_font: bool = True,
    ) -> None:
        self.title = title
        self.code_type = code_type
        self.dist_threshold = dist_threshold
        self.base_aspect_ratio = base_aspect_ratio
        self.variant_aspect_ratio = variant_aspect_ratio
        self.swatch_height = swatch_height
        self.embed_font = embed_font

    # Although this is an Exporter, it doesn't really utilise the structure set out by the base
    # class. We'll define these stubs to satisfy the type requirements, but they should never
    # actually be used.

    def format_color(self, color: Color, name: str = "") -> str:
        return f"#{color.hex}"

    def format_alias(self, name: str, target: str) -> str:
        return f"{name} -> {target}"

    def format_alias_family(self, name: str, target: str) -> list[str]:
        return [self.format_alias(name, target)]

    def format_family(self, family: ColorFamily, name: str = "") -> list[str]:
        return [f"{name}: #{family.base.hex}"]

    # --- SVG Generation Helpers ---

    def _get_code_formatter(self) -> Callable[[Color], str] | None:
        # Look up color code formatter function (e.g. hex, rgb, oklch)
        if self.code_type is None:
            return None
        ct_key = self.code_type.lower()
        if ct_key not in CODE_FORMATTERS:
            valid_types = ", ".join(CODE_FORMATTERS.keys())
            raise ValueError(
                f"Unrecognised code_type '{self.code_type}'. Expected one of: {valid_types}"
            )
        return CODE_FORMATTERS[ct_key]

    @staticmethod
    def _get_aliases(scheme: ColorScheme, color_family: ColorFamily) -> list[str]:
        # Find aliases in the scheme which point to this color family
        return [
            name
            for name, family in scheme.aliases.items()
            if family.base == color_family.base
        ]

    def _build_sections(
        self, scheme: ColorScheme
    ) -> list[list[tuple[tuple[str, ColorFamily], tuple[str, ColorFamily] | None]]]:
        # Separate the scheme into the different sections organised in a two-column layout
        # This doesn't actually construct any of the svg, just organises the colours and their names.
        # Section 1: Foreground & Background paired together
        foreground_background_section: list[
            tuple[tuple[str, ColorFamily], tuple[str, ColorFamily] | None]
        ] = [
            (("Foreground", scheme.foreground), ("Background", scheme.background))
        ]

        # Section 2: Accent colours paired two per row
        accents_section: list[
            tuple[tuple[str, ColorFamily], tuple[str, ColorFamily] | None]
        ] = []
        for i in range(0, len(scheme.accents), 2):
            left_item = (f"Accent {i + 1}", scheme.accents[i])
            right_item = (
                (f"Accent {i + 2}", scheme.accents[i + 1])
                if i + 1 < len(scheme.accents)
                else None
            )
            accents_section.append((left_item, right_item))

        # Section 3: Surface colours paired two per row
        surfaces_section: list[
            tuple[tuple[str, ColorFamily], tuple[str, ColorFamily] | None]
        ] = []
        for i in range(0, len(scheme.surfaces), 2):
            left_item = (f"Surface {i + 1}", scheme.surfaces[i])
            right_item = (
                (f"Surface {i + 2}", scheme.surfaces[i + 1])
                if i + 1 < len(scheme.surfaces)
                else None
            )
            surfaces_section.append((left_item, right_item))

        # Section 4: Auto-surface colour (if defined)
        auto_surface_section: list[
            tuple[tuple[str, ColorFamily], tuple[str, ColorFamily] | None]
        ] = []
        if scheme.auto_surface is not None:
            auto_surface_section.append((("Auto-surface", scheme.auto_surface), None))

        # return, removing any missed sections (almost certainly just surfaces_section)
        return [
            section
            for section in [
                foreground_background_section,
                accents_section,
                surfaces_section,
                auto_surface_section,
            ]
            if section
        ]

    def _calculate_layout(
        self,
        scheme: ColorScheme,
        sections: list[
            list[tuple[tuple[str, ColorFamily], tuple[str, ColorFamily] | None]]
        ],
        code_formatter: Callable[[Color], str] | None,
    ) -> _SvgLayout:
        # Just responsible for calculating the parameters needed to lay out the SVG components.

        # Default geometry & typography constants
        char_width = 7.8
        code_char_width = 6.2
        swatch_height = self.swatch_height
        base_swatch_width = round(swatch_height * self.base_aspect_ratio)
        variant_swatch_width = round(swatch_height * self.variant_aspect_ratio)
        swatch_widths = [base_swatch_width, *([variant_swatch_width] * 5)]
        swatch_corner_radius = 4
        swatch_gap = 12
        base_variant_gap = 21
        pad_x = 24
        pad_y = 20
        column_gap = 32
        row_gap = 18
        separator_gap = 36
        alias_line_height = 15

        # Find longest label text (including aliases) to size the label column
        # This is shared between the two columns of colours
        all_label_strings: list[str] = ["Colour:"] # Always included as the header
        for section in sections:
            for row in section:
                for item in row:
                    if item:
                        name, color_family = item
                        all_label_strings.append(f"{name}:")
                        for alias in self._get_aliases(scheme, color_family):
                            all_label_strings.append(f"({alias.capitalize()})")

        max_label_chars = max((len(s) for s in all_label_strings), default=10)
        label_width = int(max_label_chars * char_width + 12)

        # Accommodate color codes wider than swatches by expanding inter-swatch padding
        overflow_base = 0
        overflow_variant = 0
        if code_formatter is not None:
            max_code_len = 0
            for section in sections:
                for row in section:
                    for item in row:
                        if item:
                            _, color_family = item
                            for color in color_family:
                                max_code_len = max(
                                    max_code_len, len(code_formatter(color))
                                )
            code_width = int(math.ceil(max_code_len * code_char_width))
            if code_width > base_swatch_width:
                overflow_base = code_width - base_swatch_width
            if code_width > variant_swatch_width:
                overflow_variant = code_width - variant_swatch_width

        # Half the overflow from each adjacent swatch
        swatch_gap += overflow_variant
        # gap between the base swatch and the variant swatch increases partially due to the base
        # swatch overflow and partially due to the variant swatch overflow
        base_variant_gap += round(overflow_base / 2 + overflow_variant / 2)
        side_padding_left = round(overflow_base / 2)
        side_padding_right = round(overflow_variant / 2)

        # Find relative X offsets for the 6 swatches (base + 5 variants) within each block
        swatch_offsets = [label_width + side_padding_left]
        swatch_offsets.append(swatch_offsets[0] + base_swatch_width + base_variant_gap)
        for _ in range(1, 5):
            swatch_offsets.append(swatch_offsets[-1] + variant_swatch_width + swatch_gap)

        # Find block and canvas width
        swatches_width = (
            swatch_offsets[-1] + variant_swatch_width + side_padding_right - label_width
        )
        block_width = label_width + swatches_width
        total_width = pad_x * 2 + block_width * 2 + column_gap

        left_column_x = pad_x
        right_column_x = pad_x + block_width + column_gap

        return _SvgLayout(
            base_swatch_width=base_swatch_width,
            variant_swatch_width=variant_swatch_width,
            swatch_height=swatch_height,
            swatch_corner_radius=swatch_corner_radius,
            label_width=label_width,
            total_width=total_width,
            left_column_x=left_column_x,
            right_column_x=right_column_x,
            swatch_offsets=swatch_offsets,
            swatch_widths=swatch_widths,
            pad_x=pad_x,
            pad_y=pad_y,
            column_gap=column_gap,
            row_gap=row_gap,
            separator_gap=separator_gap,
            alias_line_height=alias_line_height,
            char_width=char_width,
            code_char_width=code_char_width,
        )

    def _render_style(self) -> str:
        # Inline minimal WOFF2 subset of Fira Code defined in `_fonts.py`
        font_stack = (
            "'Fira Code', 'Fira Mono', ui-monospace, 'SF Mono', "
            "'Roboto Mono', 'Cascadia Code', 'DejaVu Sans Mono', Menlo, "
            "Consolas, monospace"
        )
        classes = (
            ".pyg-palette-label, .pyg-palette-code, .pyg-palette-title, "
            ".pyg-palette-subtitle, .pyg-palette-header"
        )
        if not self.embed_font:
            return (
                "  <style>\n"
                f"    {classes} {{\n"
                f"      font-family: {font_stack};\n"
                "    }\n"
                "  </style>"
            )
        return (
            "  <style>\n"
            "    @font-face {\n"
            "      font-family: 'Fira Code';\n"
            "      font-style: normal;\n"
            "      font-weight: 400 700;\n"
            f"      src: url('data:font/woff2;charset=utf-8;base64,{FIRA_CODE_WOFF2_BASE64}') format('woff2');\n"
            "    }\n"
            f"    {classes} {{\n"
            f"      font-family: {font_stack};\n"
            "    }\n"
            "  </style>"
        )

    # --- SVG Element Construction Helpers ---

    @staticmethod
    def _format_svg_value(val: Any) -> str:
        # Format coordinate numbers, opacities, and string attributes for SVG
        if isinstance(val, float):
            if val.is_integer():
                return str(int(val))
            formatted = f"{val:.4f}".rstrip("0").rstrip(".")
            return formatted if formatted else "0"
        return html.escape(str(val), quote=True)

    @staticmethod
    def _svg_element(
        tag: str,
        content: str | None = None,
        class_: str | list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        # Build generic SVG element with attributes converted from snake_case to kebab-case
        attr_dict: dict[str, Any] = {}

        # Geometry and positioning attributes ordered first if present
        for geometry_key in (
            "x",
            "y",
            "x1",
            "y1",
            "x2",
            "y2",
            "width",
            "height",
            "rx",
            "ry",
            "text-anchor",
        ):
            if geometry_key in kwargs:
                attr_dict[geometry_key] = kwargs.pop(geometry_key)

        class_val = class_
        if class_val is None:
            if "class" in kwargs:
                class_val = kwargs.pop("class")
            elif "cls" in kwargs:
                class_val = kwargs.pop("cls")

        if class_val is not None:
            if isinstance(class_val, (list, tuple)):
                attr_dict["class"] = " ".join(str(item) for item in class_val)
            else:
                attr_dict["class"] = str(class_val)

        for k, v in kwargs.items():
            if v is not None:
                attr_name = k.replace("_", "-")
                attr_dict[attr_name] = v

        attrs_str = "".join(
            f' {k}="{SvgExporter._format_svg_value(v)}"'
            for k, v in attr_dict.items()
        )

        if content is None:
            return f"<{tag}{attrs_str} />"
        return f"<{tag}{attrs_str}>{content}</{tag}>"

    @staticmethod
    def _svg_text(
        text: str,
        x: float | str,
        y: float | str,
        anchor: str = "middle",
        class_: str | list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        # Construct SVG <text> element with alignment and optional styling classes
        attrs: dict[str, Any] = {"x": x, "y": y}
        if "text_anchor" in kwargs:
            anchor = kwargs.pop("text_anchor")
        elif "text-anchor" in kwargs:
            anchor = kwargs.pop("text-anchor")
        if anchor is not None:
            attrs["text-anchor"] = anchor
        attrs.update(kwargs)
        return SvgExporter._svg_element(
            "text",
            content=html.escape(str(text)),
            class_=class_,
            **attrs,
        )

    @staticmethod
    def _svg_rect(
        x: float | str | None = None,
        y: float | str | None = None,
        width: float | str | None = None,
        height: float | str | None = None,
        rx: float | str | None = None,
        corner_radius: float | str | None = None,
        fill: str | None = None,
        class_: str | list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        # Construct SVG <rect> element with geometry, corner radius, and fill
        attrs: dict[str, Any] = {}
        if x is not None:
            attrs["x"] = x
        if y is not None:
            attrs["y"] = y
        if width is not None:
            attrs["width"] = width
        if height is not None:
            attrs["height"] = height
        radius = rx if rx is not None else corner_radius
        if radius is not None:
            attrs["rx"] = radius
        if fill is not None:
            attrs["fill"] = fill
        attrs.update(kwargs)
        return SvgExporter._svg_element("rect", class_=class_, **attrs)

    @staticmethod
    def _svg_line(
        x1: float | str,
        y1: float | str,
        x2: float | str,
        y2: float | str,
        stroke: str | None = None,
        stroke_width: float | str | None = None,
        stroke_opacity: float | str | None = None,
        class_: str | list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        # Construct SVG <line> divider element with stroke styling
        attrs: dict[str, Any] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        if stroke is not None:
            attrs["stroke"] = stroke
        if stroke_width is not None:
            attrs["stroke-width"] = stroke_width
        if stroke_opacity is not None:
            attrs["stroke-opacity"] = stroke_opacity
        attrs.update(kwargs)
        return SvgExporter._svg_element("line", class_=class_, **attrs)

    def _render_header(
        self,
        layout: _SvgLayout,
        scheme: ColorScheme,
        fg_hex: str,
        start_y: float,
    ) -> tuple[list[str], float]:
        elements: list[str] = []
        current_y = start_y

        # Determine scheme name (title line) and variant (subtitle line)
        scheme_title = self.title
        if scheme_title is None:
            if scheme.name:
                scheme_title = scheme.name.replace("_", " ").title()
            else:
                scheme_title = "Colour Scheme"

        variant_label = (
            scheme._scheme_type.value.title() if hasattr(scheme, "_scheme_type") else ""
        )

        # Centered title and subtitle
        if scheme_title:
            elements.append(
                "  "
                + self._svg_text(
                    scheme_title,
                    x=layout.total_width / 2,
                    y=current_y,
                    anchor="middle",
                    class_="pyg-palette-title",
                    font_size=16,
                    font_weight="bold",
                    fill=fg_hex,
                )
            )
            if variant_label:
                current_y += 18
                elements.append(
                    "  "
                    + self._svg_text(
                        f"({variant_label})",
                        x=layout.total_width / 2,
                        y=current_y,
                        anchor="middle",
                        class_="pyg-palette-subtitle",
                        font_size=12,
                        fill=fg_hex,
                        fill_opacity=0.75,
                    )
                )
                current_y += 14
            else:
                current_y += 24
        else:
            current_y += 8

        # Column headers for left and right blocks (Colour, Base, 1..5)
        header_y = current_y + 10
        for origin_x in [layout.left_column_x, layout.right_column_x]:
            elements.append(
                "  "
                + self._svg_text(
                    "Colour",
                    x=origin_x + layout.label_width - 8,
                    y=header_y,
                    anchor="end",
                    class_="pyg-palette-header",
                    font_size=layout.header_font_size,
                    font_weight="bold",
                    fill=fg_hex,
                    fill_opacity=0.75,
                )
            )
            elements.append(
                "  "
                + self._svg_text(
                    "Base",
                    x=origin_x + layout.swatch_offsets[0] + layout.base_swatch_width / 2,
                    y=header_y,
                    anchor="middle",
                    class_="pyg-palette-header",
                    font_size=layout.header_font_size,
                    font_weight="bold",
                    fill=fg_hex,
                    fill_opacity=0.75,
                )
            )
            for i in range(1, 6):
                elements.append(
                    "  "
                    + self._svg_text(
                        str(i),
                        x=origin_x + layout.swatch_offsets[i] + layout.variant_swatch_width / 2,
                        y=header_y,
                        anchor="middle",
                        class_="pyg-palette-header",
                        font_size=layout.header_font_size,
                        font_weight="bold",
                        fill=fg_hex,
                        fill_opacity=0.75,
                    )
                )

        # Horizontal rule below headers
        header_line_y = header_y + 9
        elements.append(
            "  "
            + self._svg_line(
                x1=layout.pad_x,
                y1=header_line_y,
                x2=layout.total_width - layout.pad_x,
                y2=header_line_y,
                stroke=fg_hex,
                stroke_opacity=0.22,
                stroke_width=1,
            )
        )
        return elements, header_line_y + 18

    def _render_separator(
        self, layout: _SvgLayout, fg_hex: str, cur_y: float
    ) -> list[str]:
        # Subtle horizontal divider line centered between sections
        separator_y = cur_y + layout.separator_gap / 2
        return [
            "  "
            + self._svg_line(
                x1=layout.pad_x,
                y1=separator_y,
                x2=layout.total_width - layout.pad_x,
                y2=separator_y,
                stroke=fg_hex,
                stroke_opacity=0.18,
                stroke_width=1,
            )
        ]

    def _render_swatch(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        corner_radius: float,
        color: Color,
        bg_color: Color,
        border_color: str,
    ) -> str:
        # Subtle stroke indication if the swatch is nearly indistinguishable from background
        needs_border = color.distance_to(bg_color) < self.dist_threshold
        return (
            "  "
            + self._svg_rect(
                x=x,
                y=y,
                width=width,
                height=height,
                rx=corner_radius,
                fill=color.css,
                stroke=border_color if needs_border else None,
                stroke_width=1 if needs_border else None,
                class_="pyg-palette-swatch",
                data_hex=color.css,
            )
        )

    def _render_family(
        self,
        origin_x: int,
        y: float,
        item: tuple[str, ColorFamily],
        layout: _SvgLayout,
        scheme: ColorScheme,
        code_formatter: Callable[[Color], str] | None,
    ) -> tuple[float, list[str]]:
        name, color_family = item
        fg_hex = scheme.foreground.base.css
        bg_color = scheme.background.base
        border_color = (
            scheme.background[3].css if len(scheme.background) > 3 else fg_hex
        )
        alias_color_hex = scheme.accents[0].base.css if scheme.accents else fg_hex

        elements: list[str] = []
        aliases = self._get_aliases(scheme, color_family)

        # Position labels: always align colour name to top of the swatches
        label_y = y + 13
        elements.append(
            "  "
            + self._svg_text(
                f"{name}:",
                x=origin_x + layout.label_width - 8,
                y=label_y,
                anchor="end",
                class_="pyg-palette-label",
                font_size=layout.font_size,
                fill=fg_hex,
            )
        )
        for alias_index, alias in enumerate(aliases):
            alias_y = label_y + (alias_index + 1) * layout.alias_line_height
            elements.append(
                "  "
                + self._svg_text(
                    f"({alias.capitalize()})",
                    x=origin_x + layout.label_width - 8,
                    y=alias_y,
                    anchor="end",
                    class_="pyg-palette-label",
                    font_size=layout.font_size,
                    fill=alias_color_hex,
                )
            )

        # Render swatches and optional color codes
        colors = [color_family.base, *color_family.variants]
        for color_index, color in enumerate(colors):
            swatch_w = layout.swatch_widths[color_index]
            swatch_x = origin_x + layout.swatch_offsets[color_index]
            elements.append(
                self._render_swatch(
                    swatch_x,
                    y,
                    swatch_w,
                    layout.swatch_height,
                    layout.swatch_corner_radius,
                    color,
                    bg_color,
                    border_color,
                )
            )
            if code_formatter is not None:
                code_text = code_formatter(color)
                elements.append(
                    "  "
                    + self._svg_text(
                        code_text,
                        x=swatch_x + swatch_w / 2,
                        y=y + layout.swatch_height + 12,
                        anchor="middle",
                        class_="pyg-palette-code",
                        font_size=layout.code_font_size,
                        fill=fg_hex,
                    )
                )

        # Row height: only expand beyond swatch block if 2+ aliases exist
        swatch_block_height = float(
            layout.swatch_height + (16 if code_formatter is not None else 0)
        )
        if len(aliases) >= 2:
            last_alias_bottom = float(
                (label_y - y) + len(aliases) * layout.alias_line_height + 3
            )
            item_height = max(swatch_block_height, last_alias_bottom)
        else:
            item_height = swatch_block_height
        return item_height, elements

    def export(self, scheme: ColorScheme) -> str:
        """
        Export the colour scheme as a complete SVG palette document.

        Parameters
        ----------
        scheme : ColorScheme
            The colour scheme to export.

        Returns
        -------
        str
            A standalone SVG displaying the scheme palette with optional
            colour codes, as a string.
        """
        bg_color = scheme.background.base
        fg_color = scheme.foreground.base
        code_formatter = self._get_code_formatter()
        sections = self._build_sections(scheme)
        layout = self._calculate_layout(scheme, sections, code_formatter)

        svg_elements: list[str] = []
        cur_y = float(layout.pad_y + 16)

        # Render header (title, variant, column headers, rule)
        header_elements, cur_y = self._render_header(
            layout, scheme, fg_color.css, cur_y
        )
        svg_elements.extend(header_elements)

        # Render sections and rows
        for section_index, section in enumerate(sections):
            # Section divider line centered between sections
            if section_index > 0:
                svg_elements.extend(self._render_separator(layout, fg_color.css, cur_y))
                cur_y += layout.separator_gap

            for row_index, (left_item, right_item) in enumerate(section):
                height_left, elements_left = self._render_family(
                    layout.left_column_x,
                    cur_y,
                    left_item,
                    layout,
                    scheme,
                    code_formatter,
                )
                svg_elements.extend(elements_left)
                height_right = 0.0
                if right_item:
                    height_right, elements_right = self._render_family(
                        layout.right_column_x,
                        cur_y,
                        right_item,
                        layout,
                        scheme,
                        code_formatter,
                    )
                    svg_elements.extend(elements_right)

                row_height = max(height_left, height_right)
                cur_y += row_height
                if row_index < len(section) - 1:
                    cur_y += layout.row_gap

        total_height = int(cur_y + layout.pad_y)

        # Assemble final SVG document
        svg = [
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="0 0 {layout.total_width} {total_height}" '
                f'width="{layout.total_width}" height="{total_height}" '
                f'data-bg="{bg_color.css}" data-fg="{fg_color.css}">'
            ),
            self._render_style(),
            "  " + self._svg_rect(width="100%", height="100%", fill=bg_color.css),
            *svg_elements,
            "</svg>",
        ]
        return "\n".join(svg)


EXPORT_REGISTRY: list[type[Exporter]] = [
    LatexExporter,
    CssExporter,
    LessExporter,
    TextualExporter,
    JavascriptExporter,
    SvgExporter,
]


def get_exporter(format_or_extension: str) -> type[Exporter] | None:
    """
    Look up an exporter class by format name or file extension.

    Parameters
    ----------
    format_or_extension : str
        Format name (e.g. 'css', 'latex') or file extension (e.g. '.css',
        '.tex').

    Returns
    -------
    type[Exporter] | None
        The matching `Exporter` subclass, or `None` if no matching exporter was
        found.
    """
    for exporter in EXPORT_REGISTRY:
        if (
            exporter.format_name == format_or_extension
            or format_or_extension in exporter.file_extensions
        ):
            return exporter

    return None


__all__ = [
    "Exporter",
    "LatexExporter",
    "CssExporter",
    "LessExporter",
    "TextualExporter",
    "JavascriptExporter",
    "SvgExporter",
    "EXPORT_REGISTRY",
    "get_exporter",
    "CODE_FORMATTERS",
]

