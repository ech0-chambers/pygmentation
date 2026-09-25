import copy
import json
from pathlib import Path
from pygmentation.colors.scheme import ColorScheme, SchemeType
from pygmentation.exceptions import SchemeNotFoundError

class SchemeRegistry:
    def __init__(self, schemes_file: Path | None = None):
        self._schemes_file = schemes_file or Path(__file__).parent / "color_schemes.json"
        self._schemes: dict[str, dict] = self._load()
        self.available = list(self._schemes.keys())

    def _load(self) -> dict[str, dict]:
        with open(self._schemes_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        user_config = Path("~/.config/pygmentation/color_schemes.json").expanduser()
        if user_config.exists():
            with open(user_config, "r", encoding="utf-8") as f:
                data.update(json.load(f))
        return data

    def get(self, name: str, variant: SchemeType = SchemeType.LIGHT) -> ColorScheme:
        if name not in self._schemes:
            raise SchemeNotFoundError(name, available=list(self._schemes.keys()))
        
        # Deep copy ensures original registry data remains pristine
        raw_data = copy.deepcopy(self._schemes[name])
        if variant.name.lower() in raw_data:
            raw_data = raw_data[variant.name.lower()]
        return ColorScheme(raw_data, variant)

    def has_scheme(self, name: str, variant: SchemeType = SchemeType.LIGHT) -> bool:
        return name in self._schemes

    def list_available(self) -> list[str]:
        return self.available

registry = SchemeRegistry()
