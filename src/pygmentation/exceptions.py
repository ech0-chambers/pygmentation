class PygmentationError(Exception):
    """Base pygmentation exception."""


class SchemeNotFoundError(PygmentationError):
    def __init__(self, scheme: str, available: list[str]):
        self.scheme = scheme
        self.available = available
        super().__init__(f"Scheme '{scheme}' not found.")
