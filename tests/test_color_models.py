import pytest
from pygmentation.colors.models import RGB, HSL, HSV, XYZ, LAB, OKLAB, OKLCH, ColorModel


@pytest.mark.parametrize(
    "model, a, b, c",
    [
        (RGB, 0, 0, 0),
        (RGB, 255, 255, 255),
        (RGB, 0x5e, 0x81, 0xac),
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
        (OKLAB, 100, 100, 100),
        (OKLAB, 59.4, -5.5, -18.75),
        (OKLCH, 0, 0, 0),
        (OKLCH, 360, 1, 1),
        (OKLCH, 59.4, 19.5, 253.4),
    ],
)
def test_instantiation(model: type[ColorModel], a: float, b: float, c: float):
    c = model(a,b,c)


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
    with pytest.raises(ValueError, match = "below minimum"):
        c = model(a,b,c)

@pytest.mark.parametrize(
    "model, a, b, c",
    [
        (RGB, 0, 300, 0),
        (HSL, 0, 2, 0),
        (HSV, 0, 2, 0),
    ],
)
def test_out_of_bounds_maximum(model: type[ColorModel], a: float, b: float, c: float):
    with pytest.raises(ValueError, match = "above maximum"):
        c = model(a,b,c)

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
    color = model(a,b,c, clamp = True)

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
    color = model(a,b,c, clamp = True)

    assert color[0] == (a if color.BOUNDS[0][1] is None else min(a, color.BOUNDS[0][1]))
    assert color[1] == (b if color.BOUNDS[1][1] is None else min(b, color.BOUNDS[1][1]))
    assert color[2] == (c if color.BOUNDS[2][1] is None else min(c, color.BOUNDS[2][1]))


@pytest.mark.parametrize(
    "r, g, b",
    [
        (0, 0, 0),  # Black
        (255, 255, 255),  # White
        (255, 0, 0),  # Primary Red
        (0, 255, 0),  # Primary Green
        (0, 0, 255),  # Primary Blue
        (46, 52, 64),  # Nord Dark background
    ],
)
def test_rgb_hsl_roundtrip(r: int, g: int, b: int):
    rgb = RGB(r, g, b)
    hsl = rgb.convert_to("hsl")
    recovered = hsl.convert_to("rgb")

    assert recovered.r == pytest.approx(r, abs=1)
    assert recovered.g == pytest.approx(g, abs=1)
    assert recovered.b == pytest.approx(b, abs=1)


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
        (0, 0, 0),  # Black
        (255, 255, 255),  # White
        (255, 0, 0),  # Primary Red
        (0, 255, 0),  # Primary Green
        (0, 0, 255),  # Primary Blue
        (46, 52, 64),  # Nord Dark background
    ],
)
def test_full_roundtrip(r: int, g: int, b: int):
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

    assert recovered.r == pytest.approx(r, abs=1)
    assert recovered.g == pytest.approx(g, abs=1)
    assert recovered.b == pytest.approx(b, abs=1)


def test_model_sequence_protocol():
    rgb = RGB(255, 128, 0)
    # 1. Indexing & slicing
    assert rgb[0] == 255
    assert rgb[1] == 128
    assert rgb[-1] == 0
    assert rgb[:2] == (255, 128)

    # 2. Length & Unpacking
    assert len(rgb) == 3
    r, g, b = rgb
    assert (r, g, b) == (255, 128, 0)


def test_bounds_snapping():
    rgb = RGB(-1e-8, 255.00001, 100, clamp=False)
    assert rgb.r == 0
    assert rgb.g == 255
    assert rgb.b == 100

def test_mutation_helpers():
    color = RGB(100, 100, 100)

    new_color = color.with_r(255)
    # Check mutation
    assert new_color.r == 255
    assert new_color.g == 100
    assert new_color.b == 100
    # Check original color is unchanged
    assert color[0] == 100
    assert color[1] == 100
    assert color[2] == 100

    new_color = color.with_g(255)
    assert new_color.r == 100
    assert new_color.g == 255
    assert new_color.b == 100
    assert color[0] == 100
    assert color[1] == 100
    assert color[2] == 100
    
    new_color = color.with_b(255)
    assert new_color.r == 100
    assert new_color.g == 100
    assert new_color.b == 255
    assert color[0] == 100
    assert color[1] == 100
    assert color[2] == 100


def test_convert_to_options_and_errors():
    rgb = RGB(255, 0, 0)
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

