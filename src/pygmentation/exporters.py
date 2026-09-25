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

        for i, auto_surface in enumerate(scheme.auto_surfaces):
            output.extend(
                self.format_family(
                    auto_surface, self.canonical_name("auto_surfaces", i)
                )
            )

        for alias_name, color in scheme.aliases.items():
            name, index = scheme.get_canonical_name(color)
            output.extend(
                self.format_alias_family(alias_name, self.canonical_name(name, index))
            )

        for alias_name, color in [
            ("error", scheme.error),
            ("warning", scheme.warning),
            ("success", scheme.success),
            ("info", scheme.info),
        ]:
            name, index = scheme.get_canonical_name(color)
            output.extend(
                self.format_alias_family(alias_name, self.canonical_name(name, index))
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
        if index is None:
            return f"{root.capitalize()}Colour"
        return f"{root.capitalize()}{index}"

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


EXPORT_REGISTRY: list[type[Exporter]] = [LatexExporter]

def get_exporter(format_or_extension: str) -> Exporter | None:
    for exporter in EXPORT_REGISTRY:
        if exporter.format_name == format_or_extension or format_or_extension in exporter.file_extensions:
            return exporter

    return None
