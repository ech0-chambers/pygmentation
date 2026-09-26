from abc import ABC, abstractmethod

from io import StringIO
from pathlib import Path
from typing import ClassVar

from .colors.color import Color
from .colors.scheme import ColorFamily, ColorScheme


class Exporter(ABC):
    format_name: ClassVar[str]
    file_extensions: ClassVar[tuple[str, ...]]

    @staticmethod
    def canonical_name(root: str, index: int | None) -> str:
        if index is None:
            return root
        return f"{root}{index}"

    @staticmethod
    def canonical_alias_name(root: str) -> str:
        return root

    @abstractmethod
    def format_color(self, color: Color, name: str) -> str:
        pass

    @abstractmethod
    def format_alias(self, name: str, target: str) -> str:
        pass

    @abstractmethod
    def format_alias_family(self, name: str, target: str) -> list[str]:
        pass

    @abstractmethod
    def format_family(self, family: ColorFamily, name: str) -> list[str]:
        pass

    def export(self, scheme: ColorScheme) -> str:
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
            name, index = scheme.get_canonical_name(color)
            output.extend(
                self.format_alias_family(self.canonical_alias_name(alias_name), self.canonical_name(name, index))
            )

        for alias_name, color in [
            ("error", scheme.error),
            ("warning", scheme.warning),
            ("success", scheme.success),
            ("info", scheme.info),
        ]:
            name, index = scheme.get_canonical_name(color)
            output.extend(
                self.format_alias_family(self.canonical_alias_name(alias_name), self.canonical_name(name, index))
            )

        return "\n".join(output)
            

    def save(self, scheme, filepath: Path | str) -> None:
        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        output = self.export(scheme)
        with open(filepath, "w+") as file:
            file.write(output)


class LatexExporter(Exporter):

    format_name: ClassVar[str] = "latex"
    file_extensions: ClassVar[tuple[str]] = (".tex", ".sty", ".cls")   

    @staticmethod
    def canonical_name(root: str, index: int | None) -> str:
        if root in ["foreground", "background"]:
            root += "Colour"
        root = "".join(r.capitalize() for r in root.split("_"))
        if root.endswith("s"):
            root =root[:-1]
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
            self.format_color(v, name=f"{name}_{i+1}")
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
        return f"{name}: #{color.hex};\n{name}-rgb: {color.r}, {color.g}, {color.b};"

    def format_family(self, family: ColorFamily, name: str) -> list[str]:
        out = []
        out.append(self.format_color(family.base, name))
        out.extend(
            self.format_color(v, name=f"{name}-{i+1}")
            for i, v in enumerate(family.variants)
        )
        return out

    def format_alias(self, name: str, target: str) -> str:
        return f"{name}: var({target});\n{name}-rgb: var({target}-rgb);"

    def format_alias_family(self, name: str, target: str) -> list[str]:
        out = []
        out.append(self.format_alias(name, target))
        for i in range(1, 6):
            out.append(self.format_alias(f"{name}-{i}", f"{target}-{i}"))
        return out

    def export(self, scheme) -> str:
        out = super().export(scheme)
        return f":root{{\n{out}\n}}"


class LessExporter(Exporter):

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
            self.format_color(v, name=f"{name}-{i+1}")
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
            name, idx = scheme.get_canonical_name(color)
            target = self.canonical_name(name, idx)
            alias = self.canonical_alias_name(alias_name)
            lines.append(self.format_alias(alias, target))

        for alias_name in ["error", "warning", "success", "info"]:
            color = getattr(scheme, alias_name)
            name, idx = scheme.get_canonical_name(color)
            target = self.canonical_name(name, idx)
            alias = self.canonical_alias_name(alias_name)
            lines.append(self.format_alias(alias, target))

        return "\n".join(lines)

    def _format_family_block(self, family: ColorFamily, indent: int) -> str:
        lines = self.format_family(family, indent=indent)
        if indent == 2:
            return "\n".join(lines).lstrip()
        return "\n".join(lines)


EXPORT_REGISTRY: list[type[Exporter]] = [
    LatexExporter,
    CssExporter,
    LessExporter,
    JavascriptExporter,
]


def get_exporter(format_or_extension: str) -> type[Exporter] | None:
    for exporter in EXPORT_REGISTRY:
        if (
            exporter.format_name == format_or_extension
            or format_or_extension in exporter.file_extensions
        ):
            return exporter

    return None
