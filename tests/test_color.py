import math
import pytest
from pygmentation.colors import Color, RGB, HSL, HSV, XYZ, LAB, OKLAB, OKLCH


def test_instantiation():
    color = Color("5e81ac")
    color = Color("5E81AC")
    color = Color("#5e81ac")
    color = Color("#5E81AC")

    color = Color(RGB(  0x5e,   0x81,   0xac  ))
    assert color.hex == "5E81AC"

    color = Color(HSL(213.07699200315582, 0.31966663376480825, 0.5215769527278424))
    assert color.hex == "5E81AC"

    color = Color(HSV(213.07699200315582, 0.45347064273463866, 0.6745128377648348))
    assert color.hex == "5E81AC"

    color = Color(XYZ(19.912744457820853, 21.05875487171577, 42.0449567030622))
    assert color.hex == "5E81AC"

    color = Color(LAB(53.0137382462204, -0.5129698671717531, -26.65055231970679))
    assert color.hex == "5E81AC"

    color = Color(OKLAB(0.5943656254329134, -0.021245269942843426, -0.07434143078831318))
    assert color.hex == "5E81AC"

    color = Color(OKLCH(0.5943656254329134, 0.07731759066731092, 254.05114037644915))
    assert color.hex == "5E81AC"



@pytest.mark.parametrize("amount", [i / 10 for i in range(1, 10)])
def test_lighten_roundtrips(amount: float):
    original = 255, 242, 229
    color = Color(RGB(*original))
    color.lighten(amount).lighten(-amount)

    assert color.r == original[0]
    assert color.g == original[1]
    assert color.b == original[2]


@pytest.mark.parametrize("amount", [i / 10 for i in range(1, 10)])
def test_darken_roundtrips(amount: float):
    original = 26, 13, 0
    color = Color(RGB(*original))
    color.darken(amount).darken(-amount)

    assert color.r == original[0]
    assert color.g == original[1]
    assert color.b == original[2]


@pytest.mark.parametrize("amount", [i / 10 for i in range(1, 10)])
def test_lighten_darken_roundtrips(amount: float):
    original = 255, 242, 229
    color = Color(RGB(*original))
    color.lighten(amount).darken(amount)

    assert color.r == original[0]
    assert color.g == original[1]
    assert color.b == original[2]


@pytest.mark.parametrize("amount", [i / 10 for i in range(1, 10)])
def test_darken_lighten_roundtrips(amount: float):
    original = 26, 13, 0
    color = Color(RGB(*original))
    color.darken(amount).lighten(amount)

    assert color.r == original[0]
    assert color.g == original[1]
    assert color.b == original[2]


def test_string_representations():
    color = Color("ff8000")
    assert color.hex == "FF8000"
    assert color.css == "#FF8000"

    color_hash = Color("#00ff88")
    assert color_hash.hex == "00FF88"
    assert color_hash.css == "#00FF88"


def test_cached_model_properties():
    color = Color("5E81AC")

    assert isinstance(color.rgb, RGB)
    assert isinstance(color.hsl, HSL)
    assert isinstance(color.hsv, HSV)
    assert isinstance(color.xyz, XYZ)
    assert isinstance(color.lab, LAB)
    assert isinstance(color.oklab, OKLAB)
    assert isinstance(color.oklch, OKLCH)

    # Are we returning the same object on subsequent access (not just same values)?
    assert color.rgb is color.rgb
    assert color.hsl is color.hsl
    assert color.hsv is color.hsv
    assert color.xyz is color.xyz
    assert color.lab is color.lab
    assert color.oklab is color.oklab
    assert color.oklch is color.oklch


def test_scalar_shortcuts():
    color = Color("5E81AC")

    assert color.r == color.rgb.r
    assert color.g == color.rgb.g
    assert color.b == color.rgb.b

    assert color.h == color.hsl.h
    assert color.s == color.hsl.s
    assert color.l == color.hsl.l


def test_channel_replacement_immutability():
    original = Color("5E81AC")

    # RGB replacements
    c_r = original.with_r(255)
    assert c_r.r == 255
    assert original.r == 0x5E
    assert c_r is not original

    c_g = original.with_g(200)
    assert c_g.g == 200
    assert original.g == 0x81

    c_b = original.with_b(50)
    assert c_b.b == 50
    assert original.b == 0xAC

    # HSL replacements
    c_h = original.with_h(120)
    assert c_h.h == pytest.approx(120, abs=1.0)
    assert original.h == pytest.approx(213.08, abs=1.0)

    c_s = original.with_s(0.8)
    assert c_s.s == pytest.approx(0.8, abs=0.02)
    assert original.s == pytest.approx(0.32, abs=0.02)

    c_l = original.with_l(0.3)
    assert c_l.l == pytest.approx(0.3, abs=0.02)
    assert original.l == pytest.approx(0.52, abs=0.02)


def test_lighten_formula_and_percentage():
    c = Color("808080")
    initial_l = c.oklab.l

    lightened = c.lighten(0.2, target_lightness=1.0)
    expected_l = initial_l + (1.0 - initial_l) * 0.2
    assert lightened.oklab.l == pytest.approx(expected_l, rel=1e-4)

    # Inputs above 1 interpreted as percentages?
    assert c.lighten(20).hex == lightened.hex

    # Custom target lightness
    custom_target = c.lighten(0.5, target_lightness=0.8)
    expected_custom = initial_l + (0.8 - initial_l) * 0.5
    assert custom_target.oklab.l == pytest.approx(expected_custom, rel=1e-4)

    # Is `tint` correctly mapped to `lighten`?
    assert c.tint(0.2).hex == lightened.hex


def test_darken_formula_and_percentage():
    c = Color("808080")
    initial_l = c.oklab.l

    darkened = c.darken(0.3, target_lightness=0.0)
    expected_l = initial_l - initial_l * 0.3
    assert darkened.oklab.l == pytest.approx(expected_l, rel=1e-4)

    # Inputs above 1 interpreted as percentages?
    assert c.darken(30).hex == darkened.hex

    # Custom target lightness
    custom_target = c.darken(0.5, target_lightness=0.2)
    expected_custom = initial_l - (initial_l - 0.2) * 0.5
    assert custom_target.oklab.l == pytest.approx(expected_custom, rel=1e-4)

    # Is `shade` correctly mapped to `darken`?
    assert c.shade(0.3).hex == darkened.hex


def test_lightness_predicates():
    black = Color("000000")
    mid_grey = Color("808080")
    white = Color("FFFFFF")

    assert black.is_darker_than(white)
    assert black.is_darker_than(mid_grey)
    assert mid_grey.is_darker_than(white)

    assert white.is_lighter_than(black)
    assert white.is_lighter_than(mid_grey)
    assert mid_grey.is_lighter_than(black)

    # Colours are not strictly lighter/darker than themselves
    assert not black.is_darker_than(black)
    assert not white.is_lighter_than(white)


def test_hue_differences():
    # Do hue_diff functions return values in the correct range, -180 to 180?
    red = Color("FF0000")
    blue = Color("0000FF")

    diff_hsl = red.hue_diff(blue)
    assert -180 <= diff_hsl <= 180
    assert red.hue_diff(blue) == pytest.approx(-blue.hue_diff(red), abs=1e-5)

    diff_oklch = red.hue_diff_oklch(blue)
    assert -180 <= diff_oklch <= 180
    assert red.hue_diff_oklch(blue) == pytest.approx(-blue.hue_diff_oklch(red), abs=1e-5)


def test_lerp_oklab_interpolation():
    c1 = Color("000000")
    c2 = Color("FFFFFF")

    # Boundary amounts
    assert c1.lerp(c2, 0.0).hex == c1.hex
    assert c1.lerp(c2, 1.0).hex == c2.hex

    # Midpoint
    mid = c1.lerp(c2, 0.5)
    expected_l = (c1.oklab.l + c2.oklab.l) / 2
    assert mid.oklab.l == pytest.approx(expected_l, abs=0.01)

    # Percentage input
    mid_pct = c1.lerp(c2, 50)
    assert mid_pct.hex == mid.hex


def test_object_equality_and_hashing():
    c1 = Color("5E81AC")
    c2 = Color("5e81ac")
    c3 = Color("#5E81AC")
    other = Color("BF616A")

    assert c1 == c2 == c3
    assert c1 != other

    # Comparisons against non-`Color` objects should return False.
    # TODO: May re-visit this. Should we attempt conversions for ColorModels? hex strings?
    assert c1 != "5E81AC"
    assert c1 != None
    assert c1 != 42
    assert c1 != RGB(0x5E, 0x81, 0xAC)

    # Hashing for set / dictionary storage
    color_set = {c1, c2, c3, other}
    assert len(color_set) == 2
    assert hash(c1) == hash(c2) == hash(c3)


def test_oklab_distance_to_formula():
    c1 = Color("BF616A")
    c2 = Color("5E81AC")

    dl = c1.oklab.l - c2.oklab.l
    da = c1.oklab.a - c2.oklab.a
    db = c1.oklab.b - c2.oklab.b
    expected = 100 * math.sqrt(dl**2 + da**2 + db**2)

    assert c1.distance_to(c2) == pytest.approx(expected, rel=1e-9)


def test_oklab_distance_to_metric_axioms():
    c1 = Color("BF616A")
    c2 = Color("5E81AC")
    c3 = Color("EBCB8B")

    # Distance to self should always be 0
    assert c1.distance_to(c1) == 0.0
    assert c2.distance_to(c2) == 0.0

    # Distance(A, B) == distance(B, A)
    assert c1.distance_to(c2) == pytest.approx(c2.distance_to(c1), rel=1e-5)

    # Distance should be positive
    assert c1.distance_to(c2) > 0.0

    # Triangle inequality: d(A, C) <= d(A, B) + d(B, C)
    assert c1.distance_to(c3) <= c1.distance_to(c2) + c2.distance_to(c3) + 1e-9


def test_distance_to_cross_type_inputs():
    c = Color("BF616A")
    target = Color("5E81AC")

    expected_dist = c.distance_to(target)

    # Hex string with and without '#'
    assert c.distance_to("5E81AC") == pytest.approx(expected_dist, rel=1e-5)
    assert c.distance_to("#5E81AC") == pytest.approx(expected_dist, rel=1e-5)

    # ColorModel instances
    assert c.distance_to(target.rgb) == pytest.approx(expected_dist, rel=1e-5)
    assert c.distance_to(target.oklab) == pytest.approx(expected_dist, rel=1e-5)
    assert c.distance_to(target.lab) == pytest.approx(expected_dist, abs=0.01)


def test_ciede2000_distance_metric_axioms():
    c1 = Color("BF616A")
    c2 = Color("5E81AC")

    # Distance to self should always be 0
    assert c1.distance_to_CIEDE2000(c1) == 0.0
    assert c2.distance_to_CIEDE2000(c2) == 0.0

    # Distance(A, B) == distance(B, A)
    assert c1.distance_to_CIEDE2000(c2) == pytest.approx(c2.distance_to_CIEDE2000(c1), rel=1e-5)

    # Distance should be positive
    assert c1.distance_to_CIEDE2000(c2) > 0.0


def test_ciede2000_cross_type_inputs():
    c = Color("BF616A")
    target = Color("5E81AC")

    expected_dist = c.distance_to_CIEDE2000(target)

    # Hex string with and without '#'
    assert c.distance_to_CIEDE2000("5E81AC") == pytest.approx(expected_dist, rel=1e-5)
    assert c.distance_to_CIEDE2000("#5E81AC") == pytest.approx(expected_dist, rel=1e-5)

    # ColorModel instances
    assert c.distance_to_CIEDE2000(target.rgb) == pytest.approx(expected_dist, rel=1e-5)
    assert c.distance_to_CIEDE2000(target.oklab) == pytest.approx(expected_dist, rel=1e-5)
    assert c.distance_to_CIEDE2000(target.lab) == pytest.approx(expected_dist, abs=0.01)


@pytest.mark.parametrize(
    "lab1, lab2, expected_delta_e",
    [
        # Sharma et al. (2005) reference benchmark test pairs
        ((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485), 2.0425),
        ((50.0, 3.1571, -77.2803), (50.0, 0.0, -82.7485), 2.8615),
        ((50.0, 2.8361, -74.0200), (50.0, 0.0, -82.7485), 3.4411),
    ],
)
def test_ciede2000_sharma_benchmarks(lab1, lab2, expected_delta_e):
    """Verify CIEDE2000 implementation against published Sharma et al. (2005) reference pairs."""
    c1 = Color(LAB(*lab1))
    c2 = Color(LAB(*lab2))
    assert c1.distance_to_CIEDE2000(c2) == pytest.approx(expected_delta_e, abs=0.001)

