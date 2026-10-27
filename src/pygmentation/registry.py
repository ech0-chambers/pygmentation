import copy
import json
from pathlib import Path
from typing import Any

from pygmentation.colors.scheme import ColorScheme, SchemeType
from pygmentation.exceptions import SchemeNotFoundError


class SchemeRegistry:
    """
    Responsible for discovering built-in and user-defined schemes, and fetching
    requested schemes.

    Parameters
    ----------
    schemes_file : Path | None, optional
        The file path in which built-in schemes are found. If `None`, the
        default installation location is assumed.
    load_user_config : bool, optional
        If `True`, the directory `~/.config/pygmentation` is checked for a file
        `color_schemes.json`, which is read and any user defined schemes are
        loaded. If `False`, this is skipped entirely and only built-in schemes
        are available.

    Attributes
    ----------
    available : list[str]
        A list of all available scheme names.
    """
    def __init__(self, schemes_file: Path | None = None, load_user_config: bool = True):
        self._schemes_file = (
            schemes_file or Path(__file__).parent / "color_schemes.json"
        )
        self._load_user_config = load_user_config
        self._schemes: dict[str, Any] | None = None

    def _ensure_loaded(self) -> None:
        if self._schemes is not None:
            return

        self._schemes = {}

        # Built-in schemes first
        if self._schemes_file.exists():
            with open(self._schemes_file, encoding="utf-8") as f:
                self._schemes.update(json.load(f))

        # User schemes
        if self._load_user_config:
            user_config = Path("~/.config/pygmentation/color_schemes.json").expanduser()
            if user_config.exists():
                with open(user_config, encoding="utf-8") as f:
                    self._schemes.update(json.load(f))

    @property
    def available(self) -> list[str]:
        self._ensure_loaded()
        assert self._schemes is not None
        return sorted(self._schemes.keys())

    def get(
        self, name: str, variant: SchemeType | str = SchemeType.LIGHT
    ) -> ColorScheme:
        """
        Retrieve and initialise a colour scheme `ColorScheme` object by name.

        Parameters
        ----------
        name : str
            The name of the colour scheme to retrieve.
        variant : SchemeType | str, optional
            The variant theme to load. This should be "light", or "dark", or
            equivalent `SchemeType` object.

        Returns
        -------
        ColorScheme
            The initialised colour scheme.

        Raises
        ------
        SchemeNotFoundError
            If the requested scheme name cannot be found.
        """
        self._ensure_loaded()
        assert self._schemes is not None
        if name not in self._schemes:
            raise SchemeNotFoundError(name, available=self.available)

        # Deep copy ensures original registry data remains pristine
        raw_data = copy.deepcopy(self._schemes[name])
        if not isinstance(variant, SchemeType):
            variant = SchemeType[str(variant).upper()]
        if variant.name.lower() in raw_data:
            raw_data = raw_data[variant.name.lower()]
        return ColorScheme(raw_data, variant, name=name)

    def register(self, name: str, data: dict[str, Any], overwrite: bool = False) -> None:
        """
        Register a new scheme from a dictionary, which can then be accessed via
        `registry.get()` as normal. Note that this does not write the scheme to
        the user's custom `color_schemes.json` file.

        Parameters
        ----------
        name : str
            The name of the new scheme.
        data : dict[str, Any]
            The dictionary defining the new scheme. See Notes for the dictionary
            structure.
        overwrite : bool, optional
            If `True`, the new `data` dict will overwrite any previously
            registered scheme with the same name. If `False`, an exception is
            raised instead.

        Raises
        ------
        ValueError
            If the requested name is already registered and `overwrite = False`.
        """
        self._ensure_loaded()
        assert self._schemes is not None
        if name in self._schemes and not overwrite:
            raise ValueError(
                f"Scheme '{name}' already exists. Use `overwrite = True` to replace."
            )
        self._schemes[name] = copy.deepcopy(data)

    def unregister(self, name: str) -> None:
        """
        Remove a scheme from the registry. Note that this does not edit the
        built-in `color_schemes.json` file, nor the user's custom
        `color_schemes.json` file.

        Parameters
        ----------
        name : str
            The name of the scheme to remove. If the registry does not have an
            entry for this name, no action is taken.
        """
        self._ensure_loaded()
        assert self._schemes is not None
        self._schemes.pop(name, None)

    def reload(self) -> None:
        """
        Re-initialise the registry from the built-in `color_schemes.json` file
        and the user's custom `color_schemes.json` file if appropriate, undoing
        any changes created by `registry.register()` or `registry.unregister()`.
        """
        self._schemes = None
        self._ensure_loaded()

    def has_scheme(self, name: str) -> bool:
        """
        Check if the registry contains a scheme with the given name.

        Parameters
        ----------
        name : str
            The scheme name to query.

        Returns
        -------
        bool
            `True` if the scheme name appears in the registry, otherwise
            `False`.
        """
        self._ensure_loaded()
        assert self._schemes is not None
        return name in self._schemes


registry = SchemeRegistry()

__all__ = [
    "SchemeRegistry",
    "registry",
]

