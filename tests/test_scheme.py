"""Unit tests for ColorFamily and ColorScheme in pygmentation.colors.scheme."""

import pytest
from pygmentation import Color, ColorFamily, ColorScheme, SchemeType

# SchemeType Enum Tests


def test_scheme_type_enum():
    assert SchemeType.LIGHT == "light"
    assert SchemeType.DARK == "dark"
    assert SchemeType.EMPTY == "empty"
    assert SchemeType("light") is SchemeType.LIGHT
    assert SchemeType["DARK"] is SchemeType.DARK


# ColorFamily Tests


def test_color_family_instantiation_and_variants():
    base = Color("5E81AC")
    family = ColorFamily(base, SchemeType.DARK)

    assert family.base == base
    assert len(family.variants) == 5
    for variant in family.variants:
        assert isinstance(variant, Color)

    # Accepts string values for both arguments
    family_str = ColorFamily("5E81AC", "dark")
    assert family_str.base == base
    assert len(family_str.variants) == 5

    # Invalid scheme type raises KeyError
    with pytest.raises(KeyError):
        ColorFamily("5E81AC", "invalid_scheme_type")


def test_color_family_subscripting_and_slicing():
    family = ColorFamily("5E81AC", SchemeType.DARK)

    # Index 0 is base
    assert family[0] == family.base

    # Indices 1 to 5 are the variants
    for i in range(1, 6):
        assert family[i] == family.variants[i - 1]

    # Slicing variants
    assert family[1:] == family.variants
    assert family[:] == [family.base] + family.variants
    assert family[0:2] == [family.base, family.variants[0]]


def test_color_family_contrast_scaling_is_main():
    # Handling of foreground and background is different, such that the lightest foreground 
    # variant is still darker than the darkest background variant in a light scheme.
    # Check that `is_main` causes a smaller range of lightness
    
    # Dark base with L < 0.2 triggers too_dark
    base_dark = Color("101010")
    family_main = ColorFamily(base_dark, SchemeType.DARK, is_main=True)
    family_accent = ColorFamily(base_dark, SchemeType.DARK, is_main=False)

    main_l_span = max(v.oklab.l for v in family_main.variants) - min(
        v.oklab.l for v in family_main.variants
    )
    accent_l_span = max(v.oklab.l for v in family_accent.variants) - min(
        v.oklab.l for v in family_accent.variants
    )
    assert accent_l_span > main_l_span

    # Light base with L > 0.9 triggers too_light
    base_light = Color("FAFAFA")
    fam_main_light = ColorFamily(base_light, SchemeType.LIGHT, is_main=True)
    fam_accent_light = ColorFamily(base_light, SchemeType.LIGHT, is_main=False)

    main_l_span_light = max(v.oklab.l for v in fam_main_light.variants) - min(
        v.oklab.l for v in fam_main_light.variants
    )
    accent_l_span_light = max(v.oklab.l for v in fam_accent_light.variants) - min(
        v.oklab.l for v in fam_accent_light.variants
    )
    assert accent_l_span_light > main_l_span_light


def test_color_family_boundary_too_light_and_too_dark():
    # Too light in LIGHT scheme should generate 5 darker variants
    white_base = Color("FFFFFF")
    family_white = ColorFamily(white_base, SchemeType.LIGHT)
    for variant in family_white.variants:
        assert variant.oklab.l <= white_base.oklab.l

    # Too dark in DARK scheme. Also check for division by zero when starting lightness is 0
    black_base = Color("000000")
    family_black = ColorFamily(black_base, SchemeType.DARK)
    for variant in family_black.variants:
        assert variant.oklab.l >= black_base.oklab.l

    # Boundary adjustments without custom variants
    assert len(family_white.variants) == 5
    assert len(family_black.variants) == 5


def test_color_family_custom_variants():
    base = Color("000000")
    custom = [
        Color("111111"),
        Color("222222"),
        Color("333333"),
        Color("444444"),
        Color("555555"),
    ]
    family = ColorFamily(base, SchemeType.DARK, variants=custom)
    assert family.variants == custom
    assert family.base == base

    # Accepts strings in variants list
    family_strs = ColorFamily(
        base,
        SchemeType.DARK,
        variants=["111111", "222222", "333333", "444444", "555555"],
    )
    assert family_strs.variants == custom

    # Must have exactly 5 variants
    with pytest.raises(ValueError, match="ColorFamily requires exactly 5 variants"):
        ColorFamily(base, SchemeType.DARK, variants=custom[:4])
    with pytest.raises(ValueError, match="ColorFamily requires exactly 5 variants"):
        ColorFamily(base, SchemeType.DARK, variants=custom + [Color("666666")])


def test_color_family_anchor_hue_blending():

    # Blue base with blue-ish dark anchor (hue diff < 30)
    base_blue = Color("5E81AC")
    dark_blue = Color("1A2B4C")
    family_blended = ColorFamily(base_blue, SchemeType.DARK, dark=dark_blue)

    # Variant should shift towards dark_blue hue
    darker_variant = family_blended.variants[0]
    assert (
        abs(darker_variant.hue_diff_oklch(dark_blue))
        <= abs(base_blue.hue_diff_oklch(dark_blue)) + 1.0
    )


def test_color_family_extremes_and_index_helper():
    # In LIGHT scheme: lightest is variants[4], darkest is variants[0]
    fam_light = ColorFamily("808080", SchemeType.LIGHT)
    assert fam_light.lightest == fam_light.variants[4]
    assert fam_light.darkest == fam_light.variants[0]

    # In DARK scheme: lightest is variants[0], darkest is variants[4]
    fam_dark = ColorFamily("808080", SchemeType.DARK)
    assert fam_dark.lightest == fam_dark.variants[0]
    assert fam_dark.darkest == fam_dark.variants[4]

    # .hex property
    assert fam_dark.hex == fam_dark.base.hex

    # .index() helper
    # Remember this is the *name* index, i.e. ForegroundColour_2 in LaTeX output has index 2
    # Not the index into the array
    assert fam_dark.index(fam_dark.base) == 0
    assert fam_dark.index(fam_dark.variants[0]) == 1
    assert fam_dark.index(fam_dark.variants[4]) == 5
    assert fam_dark.index(Color("123456")) is None


def test_color_family_equality_and_hashing():
    fam1 = ColorFamily("5E81AC", SchemeType.DARK)
    fam2 = ColorFamily("5E81AC", SchemeType.DARK)
    fam_other = ColorFamily("BF616A", SchemeType.DARK)

    assert fam1 == fam2
    assert fam1 != fam_other
    assert hash(fam1) == hash(fam2)

    # Safe comparison against non-ColorFamily objects
    assert fam1 != None
    assert fam1 != "5E81AC"
    assert fam1 != Color("5E81AC")


# ColorScheme Tests

def test_scheme_initialization_and_empty(sample_nord_dict):
    scheme = ColorScheme(sample_nord_dict, SchemeType.DARK)
    assert scheme.foreground is not None
    assert scheme.background is not None
    assert len(scheme.accents) == len(sample_nord_dict["accents"])

    # SchemeType.EMPTY
    empty_scheme = ColorScheme({}, SchemeType.EMPTY)
    assert empty_scheme.foreground is None
    assert empty_scheme.background is None
    assert empty_scheme.accents is None


def test_scheme_input_validation(sample_nord_dict):
    # Missing required keys
    for missing_key in ["foreground", "background", "accents"]:
        bad_dict = sample_nord_dict.copy()
        del bad_dict[missing_key]
        with pytest.raises(
            KeyError, match=f'Scheme must contain a "{missing_key}" key'
        ):
            ColorScheme(bad_dict, SchemeType.DARK)

    # Invalid types for foreground / background
    bad_fg = sample_nord_dict.copy()
    bad_fg["foreground"] = 123456
    with pytest.raises(ValueError, match="must be a single hex string"):
        ColorScheme(bad_fg, SchemeType.DARK)

    # Invalid type for accents
    bad_accents = sample_nord_dict.copy()
    bad_accents["accents"] = "5E81AC"
    with pytest.raises(ValueError, match="must be a list of hex strings"):
        ColorScheme(bad_accents, SchemeType.DARK)

    # Invalid accent item
    bad_acc_item = sample_nord_dict.copy()
    bad_acc_item["accents"] = ["5E81AC", 123]
    with pytest.raises(ValueError, match="must be a list of hex strings"):
        ColorScheme(bad_acc_item, SchemeType.DARK)

    # Invalid surfaces list
    bad_surfaces = sample_nord_dict.copy()
    bad_surfaces["surfaces"] = "3B4252"
    with pytest.raises(
        ValueError, match='scheme\\["surfaces"\\] must be a list of hex strings'
    ):
        ColorScheme(bad_surfaces, SchemeType.DARK)


def test_scheme_polarity_correction():

    # Inverted colors passed to LIGHT scheme (dark background, light foreground)
    inverted_light = {
        "foreground": "FFFFFF",
        "background": "000000",
        "accents": ["5E81AC"],
    }
    scheme_light = ColorScheme(inverted_light, SchemeType.LIGHT)
    # Background must be lighter than foreground in LIGHT scheme
    assert scheme_light.background.base.is_lighter_than(scheme_light.foreground.base)

    # Inverted colors passed to DARK scheme (light background, dark foreground)
    inverted_dark = {
        "foreground": "000000",
        "background": "FFFFFF",
        "accents": ["5E81AC"],
    }
    scheme_dark = ColorScheme(inverted_dark, SchemeType.DARK)
    # Foreground must be lighter than background in DARK scheme
    assert scheme_dark.foreground.base.is_lighter_than(scheme_dark.background.base)


def test_scheme_surface_ordering(sample_surfaces_dict):
    # Palette with explicit surfaces
    palette = {
        "foreground": "ECEFF4",
        "background": "2E3440",
        "accents": ["5E81AC"],
        "surfaces": ["4C566A", "3B4252", "434C5E"],
    }
    scheme_dark = ColorScheme(palette, SchemeType.DARK)
    surfaces_l = [s.base.oklab.l for s in scheme_dark.surfaces]
    # In DARK scheme, surfaces are sorted in reverse lightness order
    assert surfaces_l == sorted(surfaces_l, reverse=True)


def test_scheme_distinct_accents_filtering():
    palette = {
        "foreground": "ECEFF4",
        "background": "2E3440",
        "accents": [
            "5E81AC",
            "5E81AD",  # Visually identical to first accent (delta E < 1)
            "BF616A",  # Aurora Red (distinct)
            "A3BE8C",  # Aurora Green (distinct)
        ],
    }
    scheme = ColorScheme(palette, SchemeType.DARK)

    # Duplicate should be filtered out
    assert len(scheme._distinct_accents) == 3
    distinct_hexes = [a.base.hex for a in scheme._distinct_accents]
    assert "5E81AD" not in distinct_hexes

    # All pairs in _distinct_accents must have distance >= 15
    distinct = scheme._distinct_accents
    for i, a1 in enumerate(distinct):
        for a2 in distinct[i + 1 :]:
            assert a1.base.distance_to(a2.base) >= 15


def test_scheme_semantic_and_status_aliases(sample_nord_dict):
    scheme = ColorScheme(sample_nord_dict, SchemeType.DARK)

    # 8 Semantic aliases exist and are ColorFamily instances
    for name in [
        "red",
        "orange",
        "yellow",
        "green",
        "cyan",
        "blue",
        "purple",
        "magenta",
    ]:
        alias = getattr(scheme, name)
        assert isinstance(alias, ColorFamily)
        assert alias in scheme.accents

    # Functional aliases
    assert scheme.error == scheme.red
    assert scheme.success == scheme.green
    assert scheme.info == scheme.blue
    assert isinstance(scheme.warning, ColorFamily)

    # Warning defaults to yellow, but returns orange if yellow == green
    if scheme.yellow == scheme.green:
        assert scheme.warning == scheme.orange
    else:
        assert scheme.warning == scheme.yellow


def test_scheme_high_contrast_selection(sample_nord_dict):
    scheme = ColorScheme(sample_nord_dict, SchemeType.DARK)

    # Boundary conditions
    assert scheme.high_contrast(0) == []
    assert scheme.high_contrast(-1) == []
    assert len(scheme.high_contrast(1)) == 1
    assert scheme.high_contrast(1)[0] == scheme.accents[0]
    assert scheme.high_contrast(100) == scheme.accents

    # Standard n selection
    subset_3 = scheme.high_contrast(3)
    assert len(subset_3) == 3
    assert all(isinstance(c, ColorFamily) for c in subset_3)


def test_scheme_get_canonical_name(sample_nord_dict):
    scheme = ColorScheme(sample_nord_dict, SchemeType.DARK)

    assert scheme.get_canonical_name(scheme.foreground) == ("foreground", None)
    assert scheme.get_canonical_name(scheme.background) == ("background", None)
    assert scheme.get_canonical_name(scheme.accents[0]) == ("accents", 0)
    assert scheme.get_canonical_name(scheme.surfaces[0]) == ("surfaces", 0)
    assert scheme.get_canonical_name(scheme.auto_surface) == (
        "auto_surface",
        None,
    )

    # Unknown family returns None
    unknown = ColorFamily("123456", SchemeType.DARK)
    assert scheme.get_canonical_name(unknown) is None


# Auto-Surface Tests


def test_scheme_auto_surface_dark_scheme(sample_nord_dict):
    scheme = ColorScheme(sample_nord_dict, SchemeType.DARK)
    auto_surface = scheme.auto_surface
    bg = scheme.background.base

    assert isinstance(auto_surface, ColorFamily)
    assert len(auto_surface.variants) == 5

    # In dark scheme, auto surfaces are darker than background
    assert auto_surface.base.oklab.l < bg.oklab.l
    for v in auto_surface.variants:
        assert v.oklab.l < bg.oklab.l

    # Base is the most similar to the background
    base_dist = bg.distance_to(auto_surface.base)
    var_dists = [bg.distance_to(v) for v in auto_surface.variants]
    assert base_dist < min(var_dists)

    # Variants go from least to most similar to the background (just like accents etc)
    assert var_dists == sorted(var_dists, reverse=True)


def test_scheme_auto_surface_light_scheme():
    # Light scheme with mid-tone background (headroom >= 0.08)
    palette = {
        "foreground": "101010",
        "background": "B0B0B0",
        "accents": ["3080F0"],
    }
    scheme = ColorScheme(palette, SchemeType.LIGHT)
    auto_surface = scheme.auto_surface
    bg = scheme.background.base

    assert isinstance(auto_surface, ColorFamily)
    assert len(auto_surface.variants) == 5

    # In light scheme with headroom, auto surfaces are lighter than background
    assert auto_surface.base.oklab.l > bg.oklab.l
    for v in auto_surface.variants:
        assert v.oklab.l > bg.oklab.l

    # Base is the most similar to the background
    base_dist = bg.distance_to(auto_surface.base)
    var_dists = [bg.distance_to(v) for v in auto_surface.variants]
    assert base_dist < min(var_dists)

    # Variants go from least to most similar to the background
    assert var_dists == sorted(var_dists, reverse=True)


def test_scheme_auto_surface_headroom_flip():
    # Pure black in DARK scheme (headroom < 0.08) flips direction towards 0.2
    black_palette = {
        "foreground": "FFFFFF",
        "background": "000000",
        "accents": ["FF0000"],
    }
    scheme_dark = ColorScheme(black_palette, SchemeType.DARK)
    auto_dark = scheme_dark.auto_surface
    bg_dark = scheme_dark.background.base

    # Surfaces are generated lighter than black
    assert auto_dark.base.oklab.l > bg_dark.oklab.l
    for v in auto_dark.variants:
        assert v.oklab.l > bg_dark.oklab.l
    # All tones stay within the target 0.2 headroom boundary
    assert all(c.oklab.l <= 0.25 for c in [auto_dark.base] + auto_dark.variants)

    # Base is most similar, variants go from least to most similar
    base_dist_dark = bg_dark.distance_to(auto_dark.base)
    var_dists_dark = [bg_dark.distance_to(v) for v in auto_dark.variants]
    assert base_dist_dark < min(var_dists_dark)
    assert var_dists_dark == sorted(var_dists_dark, reverse=True)

    # Pure white in LIGHT scheme (headroom < 0.08) flips direction towards 0.85
    white_palette = {
        "foreground": "000000",
        "background": "FFFFFF",
        "accents": ["FF0000"],
    }
    scheme_light = ColorScheme(white_palette, SchemeType.LIGHT)
    auto_light = scheme_light.auto_surface
    bg_light = scheme_light.background.base

    # Surfaces are generated darker than white
    assert auto_light.base.oklab.l < bg_light.oklab.l
    for v in auto_light.variants:
        assert v.oklab.l < bg_light.oklab.l
    # All tones stay within the target 0.85 headroom boundary
    assert all(c.oklab.l >= 0.80 for c in [auto_light.base] + auto_light.variants)

    # Base is most similar, variants go from least to most similar
    base_dist_light = bg_light.distance_to(auto_light.base)
    var_dists_light = [bg_light.distance_to(v) for v in auto_light.variants]
    assert base_dist_light < min(var_dists_light)
    assert var_dists_light == sorted(var_dists_light, reverse=True)


def test_scheme_auto_surface_chroma_infusion():
    # Achromatic background (C < 0.01) borrows hue from chromatic foreground (C > 0.02)
    p_fg = {
        "foreground": "336699",  # Chromatic blue
        "background": "111111",  # Neutral dark gray (C < 0.01)
        "accents": ["888888"],
    }
    s_fg = ColorScheme(p_fg, SchemeType.DARK)
    assert (
        pytest.approx(s_fg.auto_surface.base.oklch.h, abs=1e-3)
        == s_fg.foreground.base.oklch.h
    )
    assert s_fg.auto_surface.base.oklch.c > 0.005

    # Achromatic background and foreground borrows hue from first chromatic accent
    p_acc = {
        "foreground": "EEEEEE",  # Neutral light gray (C < 0.01)
        "background": "111111",  # Neutral dark gray (C < 0.01)
        "accents": ["336699"],   # Chromatic blue (C > 0.02)
    }
    s_acc = ColorScheme(p_acc, SchemeType.DARK)
    assert (
        pytest.approx(s_acc.auto_surface.base.oklch.h, abs=1e-3)
        == s_acc.accents[0].base.oklch.h
    )
    assert s_acc.auto_surface.base.oklch.c > 0.005

    # Completely achromatic palette stays achromatic
    p_achromatic = {
        "foreground": "EEEEEE",
        "background": "111111",
        "accents": ["888888"],
    }
    s_achromatic = ColorScheme(p_achromatic, SchemeType.DARK)
    assert s_achromatic.auto_surface.base.oklch.c < 0.01


def test_scheme_auto_surface_empty_scheme():
    empty_scheme = ColorScheme({}, SchemeType.EMPTY)
    assert empty_scheme.auto_surface is None


def test_scheme_auto_surface_ordering_similarity(sample_nord_dict):
    # Tests that regardless of scheme type or headroom, base is most similar
    # to background, and variants go from least to most similar to background.
    palettes = [
        (sample_nord_dict, SchemeType.DARK),
        (
            {
                "foreground": "101010",
                "background": "B0B0B0",
                "accents": ["3080F0"],
            },
            SchemeType.LIGHT,
        ),
        (
            {
                "foreground": "FFFFFF",
                "background": "000000",
                "accents": ["FF0000"],
            },
            SchemeType.DARK,
        ),
        (
            {
                "foreground": "000000",
                "background": "FFFFFF",
                "accents": ["FF0000"],
            },
            SchemeType.LIGHT,
        ),
    ]

    for p, st in palettes:
        scheme = ColorScheme(p, st)
        auto = scheme.auto_surface
        bg = scheme.background.base

        base_dist = bg.distance_to(auto.base)
        var_dists = [bg.distance_to(v) for v in auto.variants]

        # Base is strictly the most similar (smallest distance to background)
        assert base_dist < min(var_dists)

        # Variants go from least to most similar (distances strictly decreasing)
        assert var_dists == sorted(var_dists, reverse=True)
        for d1, d2 in zip(var_dists[:-1], var_dists[1:]):
            assert d1 > d2


def test_color_family_custom_variants():
    custom_vars = ["#111111", "#222222", Color("333333"), "#444444", "#555555"]
    fam = ColorFamily("000000", SchemeType.DARK, variants=custom_vars)

    assert len(fam.variants) == 5
    assert fam.variants[0] == Color("111111")
    assert fam.variants[2] == Color("333333")
    assert fam.variants[4] == Color("555555")

    # Invalid length raises ValueError
    with pytest.raises(ValueError, match="ColorFamily requires exactly 5 variants, got 4"):
        ColorFamily("000000", SchemeType.DARK, variants=custom_vars[:4])

    with pytest.raises(ValueError, match="ColorFamily requires exactly 5 variants, got 6"):
        ColorFamily("000000", SchemeType.DARK, variants=custom_vars + ["#666666"])


def test_color_family_custom_variants_equality_and_hashing():
    base = Color("5E81AC")
    fam_generated = ColorFamily(base, SchemeType.DARK)

    custom_vars = [Color("111111"), Color("222222"), Color("333333"), Color("444444"), Color("555555")]
    fam_custom1 = ColorFamily(base, SchemeType.DARK, variants=custom_vars)
    fam_custom2 = ColorFamily(base, SchemeType.DARK, variants=custom_vars)

    # Same base but different variants are not equal
    assert fam_generated != fam_custom1
    assert hash(fam_generated) != hash(fam_custom1)

    # Identical custom variants are equal and produce same hash
    assert fam_custom1 == fam_custom2
    assert hash(fam_custom1) == hash(fam_custom2)


def test_scheme_warning_alias_fallback_when_yellow_equals_green(sample_nord_scheme):
    # When yellow and green resolve to the same accent, warning falls back to orange
    assert sample_nord_scheme.warning == sample_nord_scheme.yellow

    # Simulate yellow and green resolving to same ColorFamily
    sample_nord_scheme._aliases["yellow"] = sample_nord_scheme.green
    assert sample_nord_scheme.yellow == sample_nord_scheme.green
    assert sample_nord_scheme.warning == sample_nord_scheme.orange


def test_scheme_circular_hue_diff():
    diff = ColorScheme._circular_hue_diff
    # Basic difference
    assert diff(10, 20) == 10
    # Wraparound across 0/360
    assert diff(350, 10) == 20
    assert diff(10, 350) == 20
    # Symmetry
    assert diff(45, 90) == diff(90, 45) == 45
    # Opposite sides
    assert diff(0, 180) == 180
    assert diff(10, 190) == 180
    # Negative and >360 angles
    assert diff(-10, 10) == 20
    assert diff(370, 10) == 0


def test_scheme_in_hue_range():
    in_range = ColorScheme._in_hue_range

    # Standard range (e.g. orange: 30 to 65)
    assert in_range(45, 30, 65) is True
    assert in_range(30, 30, 65) is True
    assert in_range(65, 30, 65) is True
    assert in_range(20, 30, 65) is False
    assert in_range(80, 30, 65) is False

    # Argument order invariance (swapping h_min and h_max yields identical result)
    assert in_range(45, 65, 30) is True
    assert in_range(20, 65, 30) is False

    # Range wrapping across 0 meridian (e.g. red: 345 to 30)
    assert in_range(350, 345, 30) is True
    assert in_range(0, 345, 30) is True
    assert in_range(360, 345, 30) is True
    assert in_range(15, 345, 30) is True
    assert in_range(50, 345, 30) is False
    assert in_range(200, 345, 30) is False

    # Order invariance across 0 meridian
    assert in_range(350, 30, 345) is True
    assert in_range(15, 30, 345) is True
    assert in_range(50, 30, 345) is False

    # Negative bounds / test hues
    assert in_range(10, -15, 30) is True
    assert in_range(-5, 345, 30) is True


def test_scheme_dist_to_hue_range():
    dist = ColorScheme._dist_to_hue_range

    # Inside range -> 0
    assert dist(45, 30, 65) == 0.0
    assert dist(30, 30, 65) == 0.0
    assert dist(65, 30, 65) == 0.0

    # Outside standard range -> distance to closer boundary
    assert dist(20, 30, 65) == pytest.approx(10.0)
    assert dist(75, 30, 65) == pytest.approx(10.0)

    # Wraparound across 0 meridian (345 to 30)
    assert dist(0, 345, 30) == 0.0
    assert dist(350, 345, 30) == 0.0
    assert dist(10, 345, 30) == 0.0
    # 40 is 10 deg from 30
    assert dist(40, 345, 30) == pytest.approx(10.0)
    # 335 is 10 deg from 345
    assert dist(335, 345, 30) == pytest.approx(10.0)
