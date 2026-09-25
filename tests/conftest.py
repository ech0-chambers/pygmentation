"""Shared pytest fixtures and test data for the pygmentation test suite."""

from __future__ import annotations

from typing import Any
import pytest

from pygmentation import Color, ColorScheme, SchemeType


@pytest.fixture
def sample_flat_dict() -> dict[str, Any]:
    """Simplest color scheme dict representative of most color schemes."""
    return {
        "foreground": "161829",
        "background": "E8EADF",
        "accents": [
            "464E70",
            "590219",
            "A6445E",
            "BF9004",
            "ECD879",
            "9EB9A6",
        ],
    }


@pytest.fixture
def sample_variant_dict() -> dict[str, Any]:
    """Color scheme dict with explicit light/dark variants, and surfaces."""
    return {
        "dark": {
            "foreground": "ECEFF4",
            "background": "2E3440",
            "accents": [
                "5E81AC",
                "88C0D0",
                "81A1C1",
                "BF616A",
                "D08770",
                "EBCB8B",
                "A3BE8C",
                "B48EAD",
                "8FBCBB",
            ],
            "surfaces": [
                "3B4252",
                "434C5E",
                "4C566A",
                "D8DEE9",
                "E5E9F0",
            ],
        },
        "light": {
            "foreground": "2E3440",
            "background": "ECEFF4",
            "accents": [
                "526C91",
                "669CB8",
                "6384AA",
                "AC464F",
                "C36547",
                "E1B151",
                "86A968",
                "9E6D95",
                "6BA7A5",
            ],
            "surfaces": [
                "3B4252",
                "434C5E",
                "4C566A",
                "D8DEE9",
                "E5E9F0",
            ],
        },
    }


@pytest.fixture
def sample_nord_dict() -> dict[str, Any]:
    """Nord scheme dict"""
    return {
        "foreground": "ECEFF4",
        "background": "2E3440",
        "accents": [
            "5E81AC",
            "88C0D0",
            "81A1C1",
            "BF616A",
            "D08770",
            "EBCB8B",
            "A3BE8C",
            "B48EAD",
            "8FBCBB",
        ],
        "surfaces": [
            "3B4252",
            "434C5E",
            "4C566A",
        ],
    }


@pytest.fixture
def sample_surfaces_dict() -> dict[str, Any]:
    """Scheme with surface declaration"""
    return {
        "foreground": "071D2A",
        "background": "FFEAD2",
        "accents": [
            "80A2BF",
            "466273",
            "F2B872",
            "612139",
            "009D97",
            "DD9F4A",
        ],
        "surfaces": [
            "8C5E35",
        ],
    }


@pytest.fixture
def sample_colors() -> dict[str, Color]:
    """Common primary, secondary, and neutral colors"""
    return {
        "black": Color("000000"),
        "white": Color("FFFFFF"),
        "mid_grey": Color("808080"),
        "red": Color("FF0000"),
        "green": Color("00FF00"),
        "blue": Color("0000FF"),
        "yellow": Color("FFFF00"),
        "cyan": Color("00FFFF"),
        "magenta": Color("FF00FF"),
        "orange": Color("FFA500"),
        "nord_dark_bg": Color("2E3440"),
        "nord_dark_fg": Color("ECEFF4"),
        "nord_frost_blue": Color("5E81AC"),
        "nord_aurora_red": Color("BF616A"),
    }


@pytest.fixture
def sample_nord_scheme(sample_nord_dict: dict[str, Any]) -> ColorScheme:
    """Initialised nord scheme"""
    return ColorScheme(sample_nord_dict, scheme_type=SchemeType.DARK)


@pytest.fixture
def sample_flat_scheme(sample_flat_dict: dict[str, Any]) -> ColorScheme:
    """Initialised simple scheme"""
    return ColorScheme(sample_flat_dict, scheme_type=SchemeType.LIGHT)
