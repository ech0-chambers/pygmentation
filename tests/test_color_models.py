import pytest
from pygmentation.colors.models import RGB, HSL, XYZ, LAB, OKLAB, OKLCH


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


def test_bounds_validation_and_clamping():
    # clamp=False raises ValueError on out-of-bounds inputs
    with pytest.raises(ValueError, match="below minimum"):
        RGB(-5, 100, 100, clamp=False)
    with pytest.raises(ValueError, match="above maximum"):
        RGB(300, 100, 100, clamp=False)

    # clamp=True constrains values within valid bounds
    clamped = RGB(-10, 300, 50, clamp=True)
    assert clamped.r == 0
    assert clamped.g == 255
    assert clamped.b == 50


def test_bounds_snapping():
    rgb = RGB(-1e-8, 255.00001, 100, clamp=False)
    assert rgb.r == 0
    assert rgb.g == 255
    assert rgb.b == 100
