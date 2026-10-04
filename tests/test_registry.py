"""Unit tests for SchemeRegistry, public API facade, and domain exceptions."""

import json
from pathlib import Path

import pytest

import pygmentation
from pygmentation import (
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
        lambda self: (
            tmp_path / "nonexistent_config.json"
            if "pygmentation" in str(self)
            else self
        ),
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
# 3. Dynamic Registration, Unregistration & Reloading
# ============================================================================


def test_registry_register_and_get():
    reg = SchemeRegistry(load_user_config=False)
    data = {
        "foreground": "2E3440",
        "background": "ECEFF4",
        "accents": ["88C0D0", "81A1C1", "5E81AC"],
    }
    reg.register("ocean_breeze", data)

    assert "ocean_breeze" in reg.available
    assert reg.has_scheme("ocean_breeze") is True

    scheme = reg.get("ocean_breeze")
    assert isinstance(scheme, ColorScheme)
    assert scheme.foreground.base.hex == "2E3440"
    assert scheme.background.base.hex == "ECEFF4"
    assert len(scheme.accents) == 3

    # Mutation of original data dict should not affect registry
    data["foreground"] = "FFFFFF"
    assert reg.get("ocean_breeze").foreground.base.hex == "2E3440"


def test_registry_register_duplicate_raises_and_overwrite():
    reg = SchemeRegistry(load_user_config=False)
    initial_data = {
        "foreground": "111111",
        "background": "EEEEEE",
        "accents": ["FF0000"],
    }
    reg.register("test_dupe", initial_data)

    # Re-registering without overwrite=True must raise ValueError
    with pytest.raises(ValueError, match="already exists"):
        reg.register(
            "test_dupe",
            {"foreground": "222222", "background": "FFFFFF", "accents": ["00FF00"]},
        )

    assert reg.get("test_dupe").foreground.base.hex == "111111"

    # Re-registering with overwrite=True must update
    updated_data = {
        "foreground": "222222",
        "background": "FFFFFF",
        "accents": ["00FF00"],
    }
    reg.register("test_dupe", updated_data, overwrite=True)
    assert reg.get("test_dupe").foreground.base.hex == "222222"


def test_registry_register_nested_variants():
    reg = SchemeRegistry(load_user_config=False)
    multi_data = {
        "light": {
            "foreground": "111111",
            "background": "FFFFFF",
            "accents": ["FF0000"],
        },
        "dark": {
            "foreground": "EEEEEE",
            "background": "000000",
            "accents": ["0000FF"],
        },
    }
    reg.register("duo_scheme", multi_data)

    scheme_light = reg.get("duo_scheme", SchemeType.LIGHT)
    scheme_dark = reg.get("duo_scheme", SchemeType.DARK)

    assert scheme_light.background.base.hex == "FFFFFF"
    assert scheme_dark.background.base.hex == "000000"


def test_registry_unregister_scheme():
    reg = SchemeRegistry(load_user_config=False)
    reg.register(
        "temporary",
        {"foreground": "000000", "background": "FFFFFF", "accents": ["AAAAAA"]},
    )
    assert "temporary" in reg.available
    assert reg.has_scheme("temporary") is True

    reg.unregister("temporary")
    assert "temporary" not in reg.available
    assert reg.has_scheme("temporary") is False

    with pytest.raises(SchemeNotFoundError):
        reg.get("temporary")

    # Unregistering non-existent scheme is a safe no-op
    reg.unregister("never_existed")


def test_registry_reload(tmp_path: Path):
    custom_file = tmp_path / "schemes.json"
    custom_file.write_text(
        json.dumps(
            {
                "base_scheme": {
                    "foreground": "111111",
                    "background": "FAFAFA",
                    "accents": ["123456"],
                }
            }
        ),
        encoding="utf-8",
    )
    reg = SchemeRegistry(schemes_file=custom_file, load_user_config=False)
    assert reg.available == ["base_scheme"]

    # Register an in-memory scheme
    reg.register(
        "in_memory_transient",
        {"foreground": "000000", "background": "FFFFFF", "accents": ["ABCDEF"]},
    )
    assert "in_memory_transient" in reg.available

    # Reload clears in-memory additions and restores from disk
    reg.reload()
    assert "in_memory_transient" not in reg.available
    assert reg.available == ["base_scheme"]

    # Modify file on disk and reload
    custom_file.write_text(
        json.dumps(
            {
                "reloaded_scheme": {
                    "foreground": "222222",
                    "background": "FAFAFA",
                    "accents": ["654321"],
                }
            }
        ),
        encoding="utf-8",
    )
    reg.reload()
    assert reg.available == ["reloaded_scheme"]
    assert reg.get("reloaded_scheme").foreground.base.hex == "222222"


def test_registry_lazy_loading():
    reg = SchemeRegistry(load_user_config=False)
    assert reg._schemes is None  # Not loaded yet

    # has_scheme triggers lazy load
    assert reg.has_scheme("nord") is True
    assert reg._schemes is not None


# ============================================================================
# 4. Exception Handling
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
    assert (
        "Colour values (300, 100, 100) exceeds bounds ((0, 255), (0, 255), (0, 255))."
        in str(inv_err)
    )
    assert isinstance(inv_err, PygmentationError)


# ============================================================================
# 5. Public API Facade (src/pygmentation/__init__.py)
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
