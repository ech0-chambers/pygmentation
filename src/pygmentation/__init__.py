from . import colors, exporters, plot
from .colors.color import Color
from .colors.scheme import ColorFamily, ColorScheme, SchemeType
from .exceptions import InvalidColorError, PygmentationError, SchemeNotFoundError
from .exporters import get_exporter
from .registry import SchemeRegistry, registry

# Convenience aliases
get_scheme = registry.get
register_scheme = registry.register
unregister_scheme = registry.unregister
has_scheme = registry.has_scheme


def list_schemes() -> list[str]:
    """List all available colour scheme names."""
    return registry.available


__all__ = [
    "Color",
    "ColorFamily",
    "ColorScheme",
    "SchemeType",
    "get_scheme",
    "list_schemes",
    "register_scheme",
    "unregister_scheme",
    "has_scheme",
    "registry",
    "SchemeRegistry",
    "get_exporter",
    "PygmentationError",
    "SchemeNotFoundError",
    "InvalidColorError",
    "colors",
    "exporters",
    "plot",
]

__version__ = "0.2.0"

