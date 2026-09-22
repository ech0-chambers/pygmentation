class PygmentationError(Exception):
    """Base pygmentation exception."""


class SchemeNotFoundError(PygmentationError):
    def __init__(self, scheme: str, available: list[str]):
        self.scheme = scheme
        self.available = available
        super().__init__(f"Scheme '{scheme}' not found.")

class InvalidColorError(PygmentationError):
    def __init__(self, values: tuple[float], bounds: tuple[tuple[float]]):
        self.values = values
        self.bounds = bounds
        super().__init__(f"Colour values {self.values} exceeds bounds {self.bounds}.")
