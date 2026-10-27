class PygmentationError(Exception):
    """Base exception for all errors raised by pygmentation."""


class SchemeNotFoundError(PygmentationError):
    """
    Raised when a requested colour scheme cannot be found in the registry.

    Parameters
    ----------
    scheme : str
        The name of the requested scheme that was not found.
    available : list[str]
        List of available scheme names in the registry.

    Attributes
    ----------
    scheme : str
        The name of the requested scheme that was not found.
    available : list[str]
        List of available scheme names in the registry.
    """
    def __init__(self, scheme: str, available: list[str]):
        self.scheme = scheme
        self.available = available
        super().__init__(f"Scheme '{scheme}' not found.")


class InvalidColorError(PygmentationError):
    """
    Raised when colour channel values exceed their permissible bounds.

    Parameters
    ----------
    values : tuple[float]
        The channel values that were out of bounds.
    bounds : tuple[tuple[float]]
        The expected lower and upper bounds for each channel.

    Attributes
    ----------
    values : tuple[float]
        The channel values that were out of bounds.
    bounds : tuple[tuple[float]]
        The expected lower and upper bounds for each channel.
    """
    def __init__(self, values: tuple[float], bounds: tuple[tuple[float]]):
        self.values = values
        self.bounds = bounds
        super().__init__(f"Colour values {self.values} exceeds bounds {self.bounds}.")


__all__ = [
    "PygmentationError",
    "SchemeNotFoundError",
    "InvalidColorError",
]

