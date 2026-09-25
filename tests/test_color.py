import pytest
from pygmentation.colors import Color, RGB


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
