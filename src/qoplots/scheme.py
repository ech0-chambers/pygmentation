from pathlib import Path
from .color_scheme import ColorScheme

Scheme = ColorScheme._empty()
schemes_json = Path(__file__).parent / "color_schemes.json"