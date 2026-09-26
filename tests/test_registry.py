"""Unit tests for SchemeRegistry, public API facade, and domain exceptions."""

import json
from pathlib import Path
from unittest.mock import patch
import pytest

import pygmentation
from pygmentation import (
    Color,
    ColorFamily,
    ColorScheme,
    SchemeType,
    get_scheme,
    list_schemes,
)
from pygmentation.exceptions import (
    InvalidColorError,
    PygmentationError,
    SchemeNotFoundError,
)
from pygmentation.registry import SchemeRegistry, registry


# ============================================================================
# 1. SchemeRegistry Initialization & Configuration
# ============================================================================


def test_registry_default_initialization():
    assert len(registry.available) > 0
    assert "nord" in registry.available
    assert "twilight" in registry.available
    assert registry.list_available() == registry.available


def test_registry_custom_schemes_file(tmp_path: Path, monkeypatch):
    custom_data = {
        "custom_palette": {
            "foreground": "111111",
            "background": "EEEEEE",
            "accents": ["FF0000", "00FF00", "0000FF"],
        }
    }
    custom_file = tmp_path / "custom_schemes.json"
    custom_file.write_text(json.dumps(custom_data), encoding="utf-8")

    # Isolate from user config in home dir for testing
    monkeypatch.setattr(
        "pathlib.Path.expanduser",
        lambda self: tmp_path / "nonexistent_config.json" if "pygmentation" in str(self) else self,
    )

    custom_registry = SchemeRegistry(schemes_file=custom_file)
    assert custom_registry.available == ["custom_palette"]
    assert custom_registry.has_scheme("custom_palette")
    assert not custom_registry.has_scheme("nord")

    scheme = custom_registry.get("custom_palette")
    assert scheme.foreground.base.hex == "111111"
    assert scheme.background.base.hex == "EEEEEE"


def test_registry_user_config_overlay(tmp_path: Path, monkeypatch):
    user_config_dir = tmp_path / "config" / "pygmentation"
    user_config_dir.mkdir(parents=True)
    user_config_file = user_config_dir / "color_schemes.json"

    user_data = {
        "user_only_scheme": {
            "foreground": "222222",
            "background": "FAFAFA",
            "accents": ["123456"],
        }
    }
    user_config_file.write_text(json.dumps(user_data), encoding="utf-8")

    # Mock expanduser on user_config path
    monkeypatch.setattr(
        "pathlib.Path.expanduser",
        lambda self: user_config_file if "pygmentation" in str(self) else self,
    )

    reg = SchemeRegistry()
    assert "user_only_scheme" in reg.available
    assert reg.has_scheme("user_only_scheme")
    scheme = reg.get("user_only_scheme")
    assert scheme.foreground.base.hex == "222222"


# ============================================================================
# 2. Scheme Querying & Resolution
# ============================================================================


def test_registry_has_scheme():
    assert registry.has_scheme("nord") is True
    assert registry.has_scheme("bluetit_berries") is True
    assert registry.has_scheme("completely_nonexistent_scheme_12345") is False


def test_registry_get_flat_scheme():
    scheme = registry.get("bluetit_berries", SchemeType.LIGHT)
    assert isinstance(scheme, ColorScheme)
    assert scheme._scheme_type is SchemeType.LIGHT
    assert len(scheme.accents) > 0


def test_registry_get_nested_variant_scheme():
    scheme_dark = registry.get("nord", SchemeType.DARK)
    scheme_light = registry.get("nord", SchemeType.LIGHT)

    assert scheme_dark._scheme_type is SchemeType.DARK
    assert scheme_light._scheme_type is SchemeType.LIGHT
    # Light and dark Nord have distinct background colors
    assert scheme_dark.background.base != scheme_light.background.base


def test_registry_deep_copy_isolation():
    # Fetching scheme should not allow mutation of cached registry data
    scheme1 = registry.get("nord", SchemeType.DARK)
    original_bg = scheme1.background.base.hex

    # Directly mutate raw_data in registry schemes copy or returned object
    raw_data_copy = registry._schemes["nord"]
    assert "dark" in raw_data_copy

    scheme2 = registry.get("nord", SchemeType.DARK)
    assert scheme2.background.base.hex == original_bg


# ============================================================================
# 3. Exception Handling
# ============================================================================


def test_registry_get_unknown_scheme_raises():
    with pytest.raises(SchemeNotFoundError) as exc_info:
        registry.get("unknown_palette_xyz")

    err = exc_info.value
    assert err.scheme == "unknown_palette_xyz"
    assert err.available == registry.available
    assert "Scheme 'unknown_palette_xyz' not found." in str(err)
    assert isinstance(err, PygmentationError)


def test_exceptions_hierarchy_and_formatting():
    # PygmentationError base class
    base_err = PygmentationError("Base message")
    assert isinstance(base_err, Exception)

    # SchemeNotFoundError
    not_found = SchemeNotFoundError("foobar", ["a", "b"])
    assert not_found.scheme == "foobar"
    assert not_found.available == ["a", "b"]
    assert str(not_found) == "Scheme 'foobar' not found."
    assert isinstance(not_found, PygmentationError)

    # InvalidColorError
    inv_err = InvalidColorError((300, 100, 100), ((0, 255), (0, 255), (0, 255)))
    assert inv_err.values == (300, 100, 100)
    assert inv_err.bounds == ((0, 255), (0, 255), (0, 255))
    assert "Colour values (300, 100, 100) exceeds bounds ((0, 255), (0, 255), (0, 255))." in str(inv_err)
    assert isinstance(inv_err, PygmentationError)


# ============================================================================
# 4. Public API Facade (src/pygmentation/__init__.py)
# ============================================================================


def test_public_api_get_and_list_schemes():
    assert get_scheme == registry.get
    assert list_schemes == registry.list_available

    scheme = get_scheme("nord", SchemeType.DARK)
    assert isinstance(scheme, ColorScheme)
    assert "nord" in list_schemes()


def test_public_api_exports():
    expected_exports = [
        "Color",
        "ColorFamily",
        "ColorScheme",
        "SchemeType",
        "get_scheme",
        "list_schemes",
        "PygmentationError",
        "SchemeNotFoundError",
    ]
    for sym in expected_exports:
        assert hasattr(pygmentation, sym)
        assert sym in pygmentation.__all__

    assert hasattr(pygmentation, "__version__")
    assert isinstance(pygmentation.__version__, str)
