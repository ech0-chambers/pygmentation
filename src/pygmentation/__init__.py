from .colors.color import Color
from .colors.scheme import ColorFamily, ColorScheme, SchemeType
from .exceptions import PygmentationError, SchemeNotFoundError
from .registry import registry

# aliases for backwards compatibility
get_scheme = registry.get
list_schemes = registry.list_available

__all__ = [
    "Color",
    "ColorFamily",
    "ColorScheme",
    "SchemeType",
    "get_scheme",
    "list_schemes",
    "PygmentationError",
    "SchemeNotFoundError",
]

__version__ = "0.2.0"
