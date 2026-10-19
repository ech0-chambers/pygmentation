import pytest

from pygmentation.colors.models import (
    _RGB_255,
    HSL,
    HSV,
    LAB,
    OKLAB,
    OKLCH,
    RGB,
    XYZ,
    ColorModel,
)


@pytest.mark.parametrize(
    "model, a, b, c",
    [
        (RGB, 0.0, 0.0, 0.0),
        (RGB, 1.0, 1.0, 1.0),
        (RGB, 0.3686, 0.5059, 0.6745),
        (HSL, 0, 0, 0),
        (HSL, 360, 1, 1),
        (HSL, 213, 0.32, 0.52),
        (HSV, 0, 0, 0),
        (HSV, 360, 1, 1),
        (HSV, 213, 0.46, 0.67),
        (XYZ, 0, 0, 0),
        (XYZ, 100, 100, 100),
        (XYZ, 19.8, 21, 42),
        (LAB, 0, 0, 0),
        (LAB, 100, 100, 100),
        (LAB, 52.591, -3.226, -21.76),
        (OKLAB, 0, 0, 0),
        (OKLAB, 1, 1, 1),
        (OKLAB, 0.594, -0.55, -0.1875),
        (OKLCH, 0, 0, 0),
        (OKLCH, 1, 1, 360),
        (OKLCH, 0.594, 0.195, 253.4),
    ],
)
def test_instantiation(model: type[ColorModel], a: float, b: float, c: float):
    c = model(a, b, c)


@pytest.mark.parametrize(
    "model, a, b, c",
    [
        (RGB, -10, 0, 0),
        (HSL, 0, -1, 0),
        (HSV, 0, -1, 0),
        (XYZ, -10, -5, 0),
        (LAB, -10, 0, 0),
        (OKLAB, -10, 0, 0),
        (OKLCH, -10, -1, 0),
    ],
)
def test_out_of_bounds_minimum(model: type[ColorModel], a: float, b: float, c: float):
    with pytest.raises(ValueError, match="below minimum"):
        c = model(a, b, c)


@pytest.mark.parametrize(
    "model, a, b, c",
    [
        (RGB, 0, 300, 0),
        (HSL, 0, 2, 0),
        (HSV, 0, 2, 0),
    ],
)
def test_out_of_bounds_maximum(model: type[ColorModel], a: float, b: float, c: float):
    with pytest.raises(ValueError, match="above maximum"):
        c = model(a, b, c)


@pytest.mark.parametrize(
    "model, a, b, c",
    [
        (RGB, -10, 0, 0),
        (HSL, 0, 0, 0),
        (HSV, 0, 0, 0),
        (XYZ, -10, -5, 0),
        (LAB, -10, 0, 0),
        (OKLAB, -10, 0, 0),
        (OKLCH, -10, 0, 0),
    ],
)
def test_clamping_minimum(model: type[ColorModel], a: float, b: float, c: float):
    color = model(a, b, c, clamp=True)

    assert color[0] == (a if color.BOUNDS[0][0] is None else max(a, color.BOUNDS[0][0]))
    assert color[1] == (b if color.BOUNDS[1][0] is None else max(b, color.BOUNDS[1][0]))
    assert color[2] == (c if color.BOUNDS[2][0] is None else max(c, color.BOUNDS[2][0]))


@pytest.mark.parametrize(
    "model, a, b, c",
    [
        (RGB, 300, 300, 0),
        (HSL, 300, 0, 2),
        (HSV, 300, 2, 0),
        (XYZ, 10, 5, 0),
        (LAB, 10, 0, 0),
        (OKLAB, 10, 0, 0),
        (OKLCH, 10, 0, 5),
    ],
)
def test_clamping_maximum(model: type[ColorModel], a: float, b: float, c: float):
    color = model(a, b, c, clamp=True)

    assert color[0] == (a if color.BOUNDS[0][1] is None else min(a, color.BOUNDS[0][1]))
    assert color[1] == (b if color.BOUNDS[1][1] is None else min(b, color.BOUNDS[1][1]))
    assert color[2] == (c if color.BOUNDS[2][1] is None else min(c, color.BOUNDS[2][1]))


@pytest.mark.parametrize(
    "r, g, b",
    [
        (0.0, 0.0, 0.0),  # Black
        (1.0, 1.0, 1.0),  # White
        (1.0, 0.0, 0.0),  # Primary Red
        (0.0, 1.0, 0.0),  # Primary Green
        (0.0, 0.0, 1.0),  # Primary Blue
        (46 / 255, 52 / 255, 64 / 255),  # Nord Dark background
    ],
)
def test_rgb_hsl_roundtrip(r: float, g: float, b: float):
    rgb = RGB(r, g, b)
    hsl = rgb.convert_to("hsl")
    recovered = hsl.convert_to("rgb")

    assert recovered.r == pytest.approx(r, abs=1e-4)
    assert recovered.g == pytest.approx(g, abs=1e-4)
    assert recovered.b == pytest.approx(b, abs=1e-4)


def test_oklab_oklch_roundtrip():
    oklab = OKLAB(0.7, 0.12, -0.15)
    oklch = OKLCH._from_oklab(oklab)
    recovered = oklch._to_oklab()

    assert recovered.l == pytest.approx(oklab.l, rel=1e-5)
    assert recovered.a == pytest.approx(oklab.a, rel=1e-5)
    assert recovered.b == pytest.approx(oklab.b, rel=1e-5)


@pytest.mark.parametrize(
    "r, g, b",
    [
        (0.0, 0.0, 0.0),  # Black
        (1.0, 1.0, 1.0),  # White
        (1.0, 0.0, 0.0),  # Primary Red
        (0.0, 1.0, 0.0),  # Primary Green
        (0.0, 0.0, 1.0),  # Primary Blue
        (46 / 255, 52 / 255, 64 / 255),  # Nord Dark background
    ],
)
def test_full_roundtrip(r: float, g: float, b: float):
    rgb = RGB(r, g, b)

    recovered = (
        rgb.convert_to("hsl")
        .convert_to("hsv")
        .convert_to("xyz")
        .convert_to("lab")
        .convert_to("oklab")
        .convert_to("oklch")
        .convert_to("rgb")
    )

    assert recovered.r == pytest.approx(r, abs=1e-3)
    assert recovered.g == pytest.approx(g, abs=1e-3)
    assert recovered.b == pytest.approx(b, abs=1e-3)


def test_model_sequence_protocol():
    rgb = RGB(1.0, 0.5, 0.0)
    # 1. Indexing & slicing
    assert rgb[0] == 1.0
    assert rgb[1] == 0.5
    assert rgb[-1] == 0.0
    assert rgb[:2] == (1.0, 0.5)

    # 2. Length & Unpacking
    assert len(rgb) == 3
    r, g, b = rgb
    assert (r, g, b) == (1.0, 0.5, 0.0)


def test_bounds_snapping():
    rgb = RGB(-1e-8, 1.000005, 0.5, clamp=False)
    assert rgb.r == 0.0
    assert rgb.g == 1.0
    assert rgb.b == 0.5


def test_mutation_helpers():
    color = RGB(0.4, 0.4, 0.4)

    new_color = color.with_r(1.0)
    # Check mutation
    assert new_color.r == 1.0
    assert new_color.g == 0.4
    assert new_color.b == 0.4
    # Check original color is unchanged
    assert color[0] == 0.4
    assert color[1] == 0.4
    assert color[2] == 0.4

    new_color = color.with_g(1.0)
    assert new_color.r == 0.4
    assert new_color.g == 1.0
    assert new_color.b == 0.4
    assert color[0] == 0.4
    assert color[1] == 0.4
    assert color[2] == 0.4

    new_color = color.with_b(1.0)
    assert new_color.r == 0.4
    assert new_color.g == 0.4
    assert new_color.b == 1.0
    assert color[0] == 0.4
    assert color[1] == 0.4
    assert color[2] == 0.4


def test_convert_to_options_and_errors():
    rgb = RGB(1.0, 0.0, 0.0)
    hsl = HSL(0, 1.0, 0.5)

    # hex and css string conversions
    assert rgb.convert_to("hex") == "FF0000"
    assert rgb.convert_to("css") == "#FF0000"
    assert hsl.convert_to("hex") == "FF0000"
    assert hsl.convert_to("css") == "#FF0000"

    # Conversion using Class rather than string
    assert rgb.convert_to(HSL).h == pytest.approx(0.0, abs=0.1)
    assert rgb.convert_to(RGB) is rgb  # Identity conversion returns self

    # Error conditions
    with pytest.raises(ValueError, match="Unknown color model: foobar"):
        rgb.convert_to("foobar")

    with pytest.raises(TypeError, match="Expected model name"):
        rgb.convert_to(12345)


def test_rgb_as_255():
    rgb = RGB(1.0, 0.5, 0.0)
    c255 = rgb.as_255
    assert isinstance(c255, _RGB_255)
    assert c255.r == 255
    assert c255.g == 128
    assert c255.b == 0
    assert c255 == (255, 128, 0)
    # Sequence unpacking
    r, g, b = c255
    assert (r, g, b) == (255, 128, 0)
    # Clamping behavior for minor out-of-range float noise
    assert RGB(1.05, -0.05, 0.5, clamp=True).as_255 == (255, 0, 128)


def test_rgb_from_255():
    # 3 separate args
    c1 = RGB.from_255(255, 128, 0)
    assert c1.r == 1.0
    assert c1.g == pytest.approx(128 / 255)
    assert c1.b == 0.0

    # Tuple argument
    c2 = RGB.from_255((255, 128, 0))
    assert c2 == c1

    # List argument
    c3 = RGB.from_255([255, 128, 0])
    assert c3 == c1

    # _RGB_255 argument
    c4 = RGB.from_255(c1.as_255)
    assert c4.as_255 == c1.as_255

    # Clamping
    clamped = RGB.from_255(300, -20, 128, clamp=True)
    assert clamped.r == 1.0
    assert clamped.g == 0.0
    assert clamped.b == pytest.approx(128 / 255)

    # Validation errors
    with pytest.raises(ValueError, match="above maximum"):
        RGB.from_255(300, 0, 0)
    with pytest.raises(ValueError, match="below minimum"):
        RGB.from_255(-10, 0, 0)
    with pytest.raises(ValueError, match="Expected 3 RGB values"):
        RGB.from_255(255, 255)
    with pytest.raises(ValueError, match="Expected 3 RGB values"):
        RGB.from_255((255, 255))


def test_rgb_hex_roundtrip():
    hex_code = "5E81AC"
    rgb = RGB.from_hex(hex_code)
    assert rgb.to_hex() == hex_code
    assert rgb.as_255 == (0x5E, 0x81, 0xAC)

    # Error conditions
    with pytest.raises(ValueError, match="Unknown color model: foobar"):
        rgb.convert_to("foobar")

    with pytest.raises(TypeError, match="Expected model name"):
        rgb.convert_to(12345)


def test_mutation_helpers_all_models():
    # HSV
    hsv = HSV(100, 0.5, 0.5)
    assert hsv.with_h(200).h == 200
    assert hsv.with_s(0.8).s == pytest.approx(0.8)
    assert hsv.with_v(0.9).v == pytest.approx(0.9)

    # XYZ
    xyz = XYZ(10, 20, 30)
    assert xyz.with_x(15).x == 15
    assert xyz.with_y(25).y == 25
    assert xyz.with_z(35).z == 35

    # LAB
    lab = LAB(50, 10, -20)
    assert lab.with_l(60).l == 60
    assert lab.with_a(15).a == 15
    assert lab.with_b(-10).b == -10

    # OKLAB
    oklab = OKLAB(0.5, 0.1, -0.1)
    assert oklab.with_l(0.6).l == pytest.approx(0.6)
    assert oklab.with_a(0.15).a == pytest.approx(0.15)
    assert oklab.with_b(-0.05).b == pytest.approx(-0.05)

    # OKLCH
    oklch = OKLCH(0.5, 0.1, 200)
    assert oklch.with_l(0.6).l == pytest.approx(0.6)
    assert oklch.with_c(0.15).c == pytest.approx(0.15)
    assert oklch.with_h(250).h == 250


def test_oklch_from_xyz_and_validation():
    # from_xyz tuple and 3 args
    xyz_tuple = (19.9, 21.1, 42.0)
    oklch_from_tuple = OKLCH.from_xyz(xyz_tuple)
    assert isinstance(oklch_from_tuple, OKLCH)

    oklch_from_args = OKLCH.from_xyz(*xyz_tuple)
    assert isinstance(oklch_from_args, OKLCH)
    assert oklch_from_args.l == pytest.approx(oklch_from_tuple.l)

    # Argument validation in _check_xyz_args
    with pytest.raises(ValueError, match="Expected 3 xyz values, but received 2"):
        OKLCH.from_xyz((10, 20))
