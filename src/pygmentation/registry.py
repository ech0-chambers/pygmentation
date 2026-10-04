import copy
import json
from pathlib import Path
from pygmentation.colors.scheme import ColorScheme, SchemeType
from pygmentation.exceptions import SchemeNotFoundError


class SchemeRegistry:
    def __init__(self, schemes_file: Path | None = None, load_user_config: bool = True):
        self._schemes_file = (
            schemes_file or Path(__file__).parent / "color_schemes.json"
        )
        self._load_user_config = load_user_config
        self._schemes: dict[str, dict] | None = None

    def _ensure_loaded(self) -> None:
        if self._schemes is not None:
            return

        self._schemes = {}

        # Built-in schemes first
        if self._schemes_file.exists():
            with open(self._schemes_file, "r", encoding="utf-8") as f:
                self._schemes.update(json.load(f))

        # User schemes
        if self._load_user_config:
            user_config = Path("~/.config/pygmentation/color_schemes.json").expanduser()
            if user_config.exists():
                with open(user_config, "r", encoding="utf-8") as f:
                    self._schemes.update(json.load(f))

    @property
    def available(self) -> list[str]:
        self._ensure_loaded()
        return sorted(self._schemes.keys())

    def get(
        self, name: str, variant: SchemeType | str = SchemeType.LIGHT
    ) -> ColorScheme:
        self._ensure_loaded()
        if name not in self._schemes:
            raise SchemeNotFoundError(name, available=self.available)

        # Deep copy ensures original registry data remains pristine
        raw_data = copy.deepcopy(self._schemes[name])
        if not isinstance(variant, SchemeType):
            variant = SchemeType[str(variant).upper()]
        if variant.name.lower() in raw_data:
            raw_data = raw_data[variant.name.lower()]
        return ColorScheme(raw_data, variant)

    def register(self, name: str, data: dict, overwrite: bool = False) -> None:
        self._ensure_loaded()
        if name in self._schemes and not overwrite:
            raise ValueError(
                f"Scheme '{name}' already exists. Use `overwrite = True` to replace."
            )
        self._schemes[name] = copy.deepcopy(data)

    def unregister(self, name: str) -> None:
        self._ensure_loaded()
        self._schemes.pop(name, None)

    def reload(self) -> None:
        self._schemes = None
        self._ensure_loaded()

    def has_scheme(self, name: str, variant: SchemeType = SchemeType.LIGHT) -> bool:
        self._ensure_loaded()
        return name in self._schemes

    def list_available(self) -> list[str]:
        return self.available


registry = SchemeRegistry()
