from __future__ import annotations
from io import StringIO

# ToDo:
# - Allow for colour dict to specify separate accent or surface colours, as well as specific colours to use as red, orange, etc. (without adding duplicate colours)
# - Amend ColorFamily to have a default, which will normally be base unless base is too similar to the light or dark color, in which case it will be a lighter or darker variant.
# - ColorScheme should take a dictionary instead of colors, foreground, background, etc. as separate arguments.

from typing import List, Tuple
import math
import numpy as np
from abc import ABC, abstractmethod

from enum import Enum

# We need to be careful with Enums because by default equality only works with the exact same enum. We want to be able to check with Enums *or* integers, especially in match/case blocks.


class EnumEx(Enum):
    # Extended enum class that allows for comparison with integers and other enums more consistently
    def __eq__(self, other):
        from enum import Enum

        # return self is other or (type(other) == Enum and self.value == other.value) or (type(other) == int and self.value == other)
        if isinstance(other, EnumEx) or isinstance(other, Enum):
            return self is other or self.value == other.value
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, str):
            return self.name.lower() == other.lower()
        return False

    def __int__(self):
        return self.value

    def __add__(self, other):
        if type(other) == type(self):
            return self.value + other.value
        return self.value + other

    def __sub__(self, other):
        if type(other) == type(self):
            return self.value - other.value
        return self.value - other

    def __mul__(self, other):
        if type(other) == type(self):
            return self.value * other.value
        return self.value * other

    def __truediv__(self, other):
        if type(other) == type(self):
            return self.value / other.value
        return self.value / other

    def __str__(self):
        return f"{self.name}: \t{self.value}"

    def __gt__(self, other):
        if type(other) == type(self):
            return self.value > other.value
        return self.value > other

    def __lt__(self, other):
        if type(other) == type(self):
            return self.value < other.value
        return self.value < other

    def __ge__(self, other):
        if type(other) == type(self):
            return self.value >= other.value
        return self.value >= other

    def __le__(self, other):
        if type(other) == type(self):
            return self.value <= other.value
        return self.value <= other

    def __ne__(self, other):
        if type(other) == type(self):
            return self.value != other.value
        return self.value != other


# Abstract base class for all color models


class ColorModel(ABC):
    # two properties *must* be set before __init__ is called: _string_format and _bounds
    def __init__(self, abc: float | List[float], b: float = None, c: float = None):
        if isinstance(abc, list) or isinstance(abc, tuple):
            _abc = list(abc)
        else:
            _abc = [abc, b, c]
        # check bounds. Each inherited class should have a _bounds property that is a list of tuples, one for each component. `None` if unbounded
        if len(self._bounds) != 3:
            raise ValueError(
                f"ColorModel._bounds should have 3 items, but has {len(self._bounds)}"
            )
        for i, (a, b) in enumerate(self._bounds):
            if a is not None and _abc[i] < a:
                # if it's only under by a small amount, we can just set it to the min value
                if a == 0:
                    _abc[i] = 0
                elif _abc[i] / a > 0.9999:
                    _abc[i] = a
                else:
                    raise ValueError(
                        f"Component {i} of {self.__class__.__name__} is out of bounds: {_abc[i]} < {a}"
                    )
            if b is not None and _abc[i] > b:
                # if it's only over by a small amount, we can just set it to the max value
                if _abc[i] / b < 1.0001:
                    _abc[i] = b
                else:
                    raise ValueError(
                        f"Component {i} of {self.__class__.__name__} is out of bounds: {_abc[i]} > {b}"
                    )
        self._a = _abc[0]
        self._b = _abc[1]
        self._c = _abc[2]

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self._a == other._a and self._b == other._b and self._c == other._c

    def __iter__(self):
        return iter((self._a, self._b, self._c))

    def __repr__(self):
        return self._string_format.format(self._a, self._b, self._c)

    @abstractmethod
    def to_full_rgb(self) -> Tuple[float]:
        # This should return a tuple of 3 floats [0,1], not ints, to maintain as much precision as possible
        pass

    @abstractmethod
    def from_full_rgb(rgb: Tuple[float]):
        # This should take a tuple of 3 floats [0,1], not ints, to maintain as much precision as possible
        pass

    def convert_to(self, new_model: str | type[ColorModel]):
        if isinstance(new_model, str):
            new_model = new_model.lower()
            if new_model == "rgb":
                return RGB.from_full_rgb(self.to_full_rgb())
            if new_model == "hsl":
                return HSL.from_full_rgb(self.to_full_rgb())
            if new_model == "hsv":
                return HSV.from_full_rgb(self.to_full_rgb())
            if new_model == "xyz":
                return XYZ.from_full_rgb(self.to_full_rgb())
            if new_model == "lab":
                return LAB.from_full_rgb(self.to_full_rgb())
            if new_model == "hex":
                r, g, b = self.to_full_rgb()
                # r,g,b need to be ints, round correctly
                r = int(round(r * 255))
                g = int(round(g * 255))
                b = int(round(b * 255))
                return f"{r:02X}{g:02X}{b:02X}"
            if new_model == "css":
                r, g, b = self.to_full_rgb()
                # r,g,b need to be ints, round correctly
                r = int(round(r * 255))
                g = int(round(g * 255))
                b = int(round(b * 255))
                return f"#{r:02X}{g:02X}{b:02X}"

            raise ValueError(f"Unknown color model: {new_model}")
        return new_model.from_full_rgb(self.to_full_rgb())

    def as_tuple(self):
        return (self._a, self._b, self._c)


class RGB(ColorModel):
    def __init__(self, rgb: int | List[int], g: int = None, b: int = None):
        self._bounds = ((0, 255), (0, 255), (0, 255))
        self._string_format = "RGB({}, {}, {})"
        # call super
        super().__init__(rgb, g, b)

    def to_full_rgb(self) -> Tuple[float]:
        return (self._a / 255, self._b / 255, self._c / 255)

    @classmethod
    def from_full_rgb(cls, rgb: Tuple[float]):
        return cls((rgb[0] * 255, rgb[1] * 255, rgb[2] * 255))

    @property
    def r(self):
        return self._a

    @property
    def g(self):
        return self._b

    @property
    def b(self):
        return self._c

    @classmethod
    def from_hex(cls, hex: str):
        return cls(tuple(int(hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)))


class HSL(ColorModel):
    def __init__(self, hsl: int | List[int], s: int = None, l: int = None):
        self._bounds = ((0, 360), (0, 1), (0, 1))
        self._string_format = "HSL({:.0f}\u00b0, {:.0%}, {:.0%})"
        if isinstance(hsl, list) or isinstance(hsl, tuple):
            hsl = list(hsl)
            hsl[0] = (
                hsl[0] % 360
            )  # pre-emtively mod 360 so that boundary checking is okay
        else:
            hsl = hsl % 360
        # call super
        super().__init__(hsl, s, l)

    def to_full_rgb(self) -> Tuple[float]:
        # https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB
        c = (1 - abs(2 * self.l - 1)) * self.s
        x = c * (1 - abs((self.h / 60) % 2 - 1))
        m = self.l - c / 2
        if self.h < 60:
            return (c + m, x + m, m)
        if self.h < 120:
            return (x + m, c + m, m)
        if self.h < 180:
            return (m, c + m, x + m)
        if self.h < 240:
            return (m, x + m, c + m)
        if self.h < 300:
            return (x + m, m, c + m)
        return (c + m, m, x + m)

    @classmethod
    def from_full_rgb(cls, rgb: Tuple[float]):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        r, g, b = rgb
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin
        if delta == 0:
            h = 0
        elif cmax == r:
            h = 60 * (((g - b) / delta) % 6)
        elif cmax == g:
            h = 60 * (((b - r) / delta) + 2)
        elif cmax == b:
            h = 60 * (((r - g) / delta) + 4)
        l = (cmax + cmin) / 2
        if delta == 0:
            s = 0
        else:
            s = delta / (1 - abs(2 * l - 1))
        return cls((h, s, l))

    @property
    def h(self):
        return self._a

    @property
    def s(self):
        return self._b

    @property
    def l(self):
        return self._c


class HSV(ColorModel):
    def __init__(self, hsv: int | List[int], s: int = None, v: int = None):
        self._bounds = ((0, 360), (0, 1), (0, 1))
        self._string_format = "HSV({:.0f}\u00b0, {:.0%}, {:.0%})"
        # call super
        super().__init__(hsv, s, v)

    def to_full_rgb(self) -> Tuple[float]:
        # https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB
        c = self.v * self.s
        x = c * (1 - abs((self.h / 60) % 2 - 1))
        m = self.v - c
        if self.h < 60:
            return (c + m, x + m, m)
        if self.h < 120:
            return (x + m, c + m, m)
        if self.h < 180:
            return (m, c + m, x + m)
        if self.h < 240:
            return (m, x + m, c + m)
        if self.h < 300:
            return (x + m, m, c + m)
        return (c + m, m, x + m)

    @classmethod
    def from_full_rgb(cls, rgb: Tuple[float]):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        r, g, b = rgb
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin
        if delta == 0:
            h = 0
        elif cmax == r:
            h = 60 * (((g - b) / delta) % 6)
        elif cmax == g:
            h = 60 * (((b - r) / delta) + 2)
        elif cmax == b:
            h = 60 * (((r - g) / delta) + 4)
        v = cmax
        if cmax == 0:
            s = 0
        else:
            s = delta / cmax
        return cls((h, s, v))

    @property
    def h(self):
        return self._a

    @property
    def s(self):
        return self._b

    @property
    def v(self):
        return self._c


class XYZ(ColorModel):
    def __init__(self, xyz: int | List[int], y: int = None, z: int = None):
        self._bounds = ((0, None), (0, None), (0, None))
        self._string_format = "XYZ({}, {}, {})"
        # call super
        super().__init__(xyz, y, z)

    def to_full_rgb(self) -> Tuple[float]:
        x, y, z = (x / 100 for x in (self.x, self.y, self.z))
        r = x * 3.2406 + y * -1.5372 + z * -0.4986
        g = x * -0.9689 + y * 1.8758 + z * 0.0415
        b = x * 0.0557 + y * -0.2040 + z * 1.0570
        r = 12.92 * r if r <= 0.0031308 else (1.055 * r ** (1 / 2.4)) - 0.055
        g = 12.92 * g if g <= 0.0031308 else (1.055 * g ** (1 / 2.4)) - 0.055
        b = 12.92 * b if b <= 0.0031308 else (1.055 * b ** (1 / 2.4)) - 0.055
        return (r, g, b)

    @classmethod
    def from_full_rgb(cls, rgb: Tuple[float]):
        r, g, b = (
            x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb
        )
        x = r * 0.4124 + g * 0.3576 + b * 0.1805
        y = r * 0.2126 + g * 0.7152 + b * 0.0722
        z = r * 0.0193 + g * 0.1192 + b * 0.9505
        return cls((x * 100, y * 100, z * 100))

    @property
    def x(self):
        return self._a

    @property
    def y(self):
        return self._b

    @property
    def z(self):
        return self._c


class LAB(ColorModel):
    def __init__(self, lab: int | List[int], a: int = None, b: int = None):
        self._bounds = ((0, None), (None, None), (None, None))
        self._string_format = "LAB({}, {}, {})"
        # call super
        super().__init__(lab, a, b)

    def _to_xyz(self) -> XYZ:
        # https://en.wikipedia.org/wiki/CIELAB_color_space
        def f(t):
            if t > 6 / 29:
                return t**3
            return (t - 4 / 29) / 7.787

        y = (self.l + 16) / 116
        x = self.a / 500 + y
        z = y - self.b / 200
        return XYZ((95.047 * f(x), 100 * f(y), 108.883 * f(z)))

    @classmethod
    def _from_xyz(cls, xyz: XYZ):
        # https://en.wikipedia.org/wiki/CIELAB_color_space
        def f(t):
            delta = 6 / 29
            if t > delta**3:
                return t ** (1 / 3)
            return t / (3 * delta**2) + 4 / 29

        Xn = 95.0489
        Yn = 100
        Zn = 108.8840
        x = f(xyz.x / Xn)
        y = f(xyz.y / Yn)
        z = f(xyz.z / Zn)
        return cls((116 * y - 16, 500 * (x - y), 200 * (y - z)))

    def to_full_rgb(self) -> Tuple[float]:
        # lab to rgb, using xyz as an intermediate step
        return self._to_xyz().to_full_rgb()

    @classmethod
    def from_full_rgb(cls, rgb: Tuple[float]):
        # rgb to lab, using xyz as an intermediate step
        return cls._from_xyz(XYZ.from_full_rgb(rgb))


class Color:
    """
    A class to represent a color, with methods to convert between color spaces.
    * hex: a hex string, not including the '#'
    * rgb: a tuple of 3 ints, each between 0 and 255
    * hsl: a tuple of 3 floats, h: 0-360, s: 0-1, l: 0-1
    * hsv: a tuple of 3 floats, h: 0-360, s: 0-1, v: 0-1
    * xyz: a tuple of 3 floats, x: 0-95.047, y: 0-100, z: 0-108.883
    * lab: a tuple of 3 floats, l: 0-100, a and b unbounded
    """

    def __init__(self, hex: str, name: str = None):
        if hex[0] == "#":
            hex = hex[1:]
        self._hex = hex
        self._name = name
        self.clear_cache()

    def clear_cache(self):
        self._rgb = None
        self._hsl = None
        self._hsv = None
        self._xyz = None
        self._lab = None

    @staticmethod
    def from_hsl(hsl: tuple | HSL):
        if isinstance(hsl, tuple) or isinstance(hsl, list):
            hsl = HSL(*hsl)
        return Color(hsl.convert_to("hex"))

    # Getters and setters

    @property
    def hex(self) -> str:
        return self._hex

    @property
    def css(self) -> str:
        return "#" + self._hex

    @hex.setter
    def hex(self, value: str):
        self._hex = value
        self.clear_cache()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def rgb(self) -> tuple:
        if self._rgb is None:
            self._rgb = RGB.from_hex(self.hex)
        return self._rgb

    @rgb.setter
    def rgb(self, value: tuple | RGB):
        if isinstance(value, tuple) or isinstance(value, list):
            value = RGB(*value)
        self._hex = value.convert_to("hex")
        self.clear_cache()

    @property
    def hsl(self) -> tuple:
        if self._hsl is None:
            self._hsl = self.rgb.convert_to("hsl")
        return self._hsl

    @hsl.setter
    def hsl(self, value: tuple | HSL):
        if isinstance(value, tuple) or isinstance(value, list):
            value = HSL(*value)
        self._hex = value.convert_to("hex")
        self.clear_cache()

    @property
    def hsv(self) -> tuple:
        if self._hsv is None:
            self._hsv = self.rgb.convert_to("hsv")
        return self._hsv

    @hsv.setter
    def hsv(self, value: tuple | HSV):
        if isinstance(value, tuple) or isinstance(value, list):
            value = HSV(*value)
        self._hex = value.convert_to("hex")
        self.clear_cache()

    @property
    def xyz(self) -> tuple:
        if self._xyz is None:
            self._xyz = self.rgb.convert_to("xyz")
        return self._xyz

    @xyz.setter
    def xyz(self, value: tuple | XYZ):
        if isinstance(value, tuple) or isinstance(value, list):
            value = XYZ(*value)
        self._hex = value.convert_to("hex")
        self.clear_cache()

    @property
    def lab(self) -> tuple:
        if self._lab is None:
            self._lab = self.rgb.convert_to("lab")
        return self._lab

    @lab.setter
    def lab(self, value: tuple | LAB):
        if isinstance(value, tuple) or isinstance(value, list):
            value = LAB(*value)
        self._hex = value.convert_to("hex")
        self.clear_cache()

    @property
    def r(self) -> int:
        return self.rgb.r

    @r.setter
    def r(self, value: int):
        self.rgb = RGB(value, self.g, self.b)

    @property
    def g(self) -> int:
        return self.rgb.g

    @g.setter
    def g(self, value: int):
        self.rgb = RGB(self.r, value, self.b)

    @property
    def b(self) -> int:
        return self.rgb.b

    @b.setter
    def b(self, value: int):
        self.rgb = RGB(self.r, self.g, value)

    @property
    def h(self) -> int:
        return self.hsl.h

    @h.setter
    def h(self, value: int):
        self.hsl = HSL(value, self.s, self.l)

    @property
    def s(self) -> int:
        return self.hsl.s

    @s.setter
    def s(self, value: int):
        self.hsl = HSL(self.h, value, self.l)

    @property
    def l(self) -> int:
        return self.hsl.l

    @l.setter
    def l(self, value: int):
        self.hsl = HSL(self.h, self.s, value)

    @property
    def h_hsv(self) -> int:
        return self.hsv.h

    @h_hsv.setter
    def h_hsv(self, value: int):
        self.hsv = HSV(value, self.s_hsv, self.v)

    @property
    def s_hsv(self) -> int:
        return self.hsv.s

    @s_hsv.setter
    def s_hsv(self, value: int):
        self.hsv = HSV(self.h_hsv, value, self.v)

    @property
    def v(self) -> int:
        return self.hsv.v

    @v.setter
    def v(self, value: int):
        self.hsv = HSV(self.h_hsv, self.s_hsv, value)

    @property
    def v_hsv(self) -> int:
        return self.v

    @v_hsv.setter
    def v_hsv(self, value: int):
        self.v = value

    @property
    def x(self) -> int:
        return self.xyz.x

    @x.setter
    def x(self, value: int):
        self.xyz = XYZ(value, self.y, self.z)

    @property
    def y(self) -> int:
        return self.xyz.y

    @y.setter
    def y(self, value: int):
        self.xyz = XYZ(self.x, value, self.z)

    @property
    def z(self) -> int:
        return self.xyz.z

    @z.setter
    def z(self, value: int):
        self.xyz = XYZ(self.x, self.y, value)

    @property
    def l_lab(self) -> int:
        return self.lab.l

    @l_lab.setter
    def l_lab(self, value: int):
        self.lab = LAB(value, self.a, self.b_lab)

    @property
    def a(self) -> int:
        return self.lab.a

    @a.setter
    def a(self, value: int):
        self.lab = LAB(self.l_lab, value, self.b_lab)

    @property
    def a_lab(self) -> int:
        return self.a

    @a_lab.setter
    def a_lab(self, value: int):
        self.a = value

    @property
    def b_lab(self) -> int:
        return self.lab.b

    @b_lab.setter
    def b_lab(self, value: int):
        self.lab = LAB(self.l_lab, self.a, value)

    # Methods

    def lighten(
        self, amount: float, in_place: bool = False, target_lightness: float = 1
    ):
        if amount > 1:
            amount /= 100
        new_l = target_lightness - (target_lightness - self.hsl.l) * (1 - amount)
        if in_place:
            self.hsl = HSL(self.hsl.h, self.hsl.s, new_l)
        else:
            return Color(HSL(self.hsl.h, self.hsl.s, new_l).convert_to("hex"))

    def darken(
        self, amount: float, in_place: bool = False, target_lightness: float = 0
    ):
        if amount > 1:
            amount /= 100
        new_l = target_lightness + (self.hsl.l - target_lightness) * (1 - amount)
        if in_place:
            self.hsl = HSL(self.hsl.h, self.hsl.s, new_l)
        else:
            return Color(HSL(self.hsl.h, self.hsl.s, new_l).convert_to("hex"))

    def hue_diff(self, other):
        # Return the signed difference in hue between self and other, in degrees, accounting for wrapping at 360
        return (other.hsl.h - self.hsl.h + 180) % 360 - 180

    def move_to_color(self, other, amount: float, in_place: bool = False):
        # Move self towards other by amount, in place or not, in hsl space
        if amount > 1:
            amount /= 100
        if amount == 0:
            return self
        if amount == 1:
            return other
        new_h = self.hsl.h + self.hue_diff(other) * amount
        new_s = self.hsl.s + (other.hsl.s - self.hsl.s) * amount
        new_l = self.hsl.l + (other.hsl.l - self.hsl.l) * amount
        if in_place:
            self.hsl = HSL(new_h, new_s, new_l)
        else:
            return Color(HSL(new_h, new_s, new_l).convert_to("hex"))

    def __str__(self):
        return self.to_string(format="css")

    def to_string(self, format="css"):
        return str(self.rgb.convert_to(format))

    def is_lighter_than(self, other):
        return self.hsl.l > other.hsl.l

    def is_darker_than(self, other):
        return self.hsl.l < other.hsl.l

    def distance_to(self, other):
        # Returns a measure of similarity between self and other, based on https://github.com/hamada147/IsThisColourSimilar
        def deg_to_rad(deg):
            return deg * math.pi / 180

        def rad_to_deg(rad):
            return rad * 180 / math.pi

        lab1 = self.lab
        lab2 = other.lab

        l1, a1, b1 = lab1
        l2, a2, b2 = lab2

        avgL = (l1 + l2) / 2
        c1 = math.sqrt(a1**2 + b1**2)
        c2 = math.sqrt(a2**2 + b2**2)
        avgC = (c1 + c2) / 2
        g = (1 - math.sqrt(avgC**7 / (avgC**7 + 25**7))) / 2

        a1p = a1 * (1 + g)
        a2p = a2 * (1 + g)

        c1p = math.sqrt(a1p**2 + b1**2)
        c2p = math.sqrt(a2p**2 + b2**2)

        avgCp = (c1p + c2p) / 2

        h1p = rad_to_deg(math.atan2(b1, a1p))
        if h1p < 0:
            h1p += 360

        h2p = rad_to_deg(math.atan2(b2, a2p))
        if h2p < 0:
            h2p += 360

        if abs(h1p - h2p) > 180:
            avgHp = (h1p + h2p + 360) / 2
        else:
            avgHp = (h1p + h2p) / 2

        t = (
            1
            - 0.17 * math.cos(deg_to_rad(avgHp - 30))
            + 0.24 * math.cos(deg_to_rad(2 * avgHp))
            + 0.32 * math.cos(deg_to_rad(3 * avgHp + 6))
            - 0.2 * math.cos(deg_to_rad(4 * avgHp - 63))
        )

        deltaHp = h2p - h1p
        if abs(deltaHp) > 180:
            if h2p <= h1p:
                deltaHp += 360
            else:
                deltaHp -= 360

        deltaLp = l2 - l1
        deltaCp = c2p - c1p
        deltaHp = 2 * math.sqrt(c1p * c2p) * math.sin(deg_to_rad(deltaHp) / 2)

        sL = 1 + ((0.015 * (avgL - 50) ** 2) / math.sqrt(20 + (avgL - 50) ** 2))
        sC = 1 + 0.045 * avgCp
        sH = 1 + 0.015 * avgCp * t

        deltaRho = 30 * math.exp(-(((avgHp - 275) / 25) ** 2))
        rc = 2 * math.sqrt((avgCp**7) / (avgCp**7 + 25**7))
        rt = -rc * math.sin(2 * deg_to_rad(deltaRho))

        kl = 1
        kc = 1
        kh = 1

        deltaE = math.sqrt(
            (deltaLp / (kl * sL)) ** 2
            + (deltaCp / (kc * sC)) ** 2
            + (deltaHp / (kh * sH)) ** 2
            + rt * (deltaCp / (kc * sC)) * (deltaHp / (kh * sH))
        )

        return deltaE

    def __eq__(self, other):
        return self.hex == other.hex

    def __hash__(self):
        return hash(self.hex)


class SchemeType(EnumEx):
    EMPTY = 0
    LIGHT = 1
    DARK = 2


class ColorFamily:

    def __init__(
        self,
        base: Color | str,
        light: Color | str = None,
        dark: Color | str = None,
        scheme_type: SchemeType | str = SchemeType.LIGHT,
        force_variants: bool = False,
        name=None,
    ):
        if isinstance(base, str):
            base = Color(base)
        if light is not None:
            if isinstance(light, str):
                light = Color(light)
        else:
            light = Color("FFFFFF")
        if dark is not None:
            if isinstance(dark, str):
                dark = Color(dark)
        else:
            dark = Color("000000")
        if isinstance(scheme_type, str):
            if scheme_type.lower() == "light":
                scheme_type = SchemeType.LIGHT
            elif scheme_type.lower() == "dark":
                scheme_type = SchemeType.DARK
            else:
                raise ValueError(f"Invalid scheme type '{scheme_type}'")
        if light is not None and dark is not None:
            if light.is_darker_than(dark):
                light, dark = dark, light

        self._base = base
        self._light = light
        self._dark = dark
        self._scheme_type = scheme_type
        self._name = name

        use_dark = False  # If True we'll use the light color as a target when lightening, otherwise we'll only change hsl.l
        use_light = False  # If True we'll use the dark color as a target when darkening, otherwise we'll only change hsl.l

        if self._light is not None:
            use_light = abs(self._base.hue_diff(self._light)) < 30
        if self._dark is not None:
            use_dark = abs(self._base.hue_diff(self._dark)) < 30

        too_light = not (force_variants) and (
            (not use_light and self._base.l > 0.8)
            or (use_light and self._base.l / self._light.l > 0.95)
        )
        too_dark = not (force_variants) and (
            (not use_dark and self._base.l < 0.2)
            or (use_dark and self._base.l > 0 and self._dark.l / self._base.l > 0.95)
        )

        amounts = [0] * 5

        if self._scheme_type == SchemeType.LIGHT:
            if too_light:
                amounts = [-0.9, -0.75, -0.5, -0.25, -0.1]
            elif too_dark:
                amounts = [0.1, 0.25, 0.5, 0.75, 0.9]
            else:
                amounts = [-0.5, -0.25, 0.4, 0.6, 0.8]
        elif self._scheme_type == SchemeType.DARK:
            if too_light:
                amounts = [-0.1, -0.25, -0.5, -0.75, -0.9]
            elif too_dark:
                amounts = [0.9, 0.75, 0.5, 0.25, 0.1]
            else:
                amounts = [0.5, 0.25, -0.4, -0.6, -0.8]
        else:
            raise ValueError(f"Invalid scheme type '{self._scheme_type}'")

        self.variants = []
        for amount in amounts:
            if amount < 0:
                if use_dark:
                    self.variants.append(self._base.move_to_color(self._dark, -amount))
                else:
                    self.variants.append(
                        self._base.darken(
                            -amount, target_lightness=min(self._dark.l, 0.2)
                        )
                    )
            elif amount > 0:
                if use_light:
                    self.variants.append(self._base.move_to_color(self._light, amount))
                else:
                    self.variants.append(
                        self._base.lighten(
                            amount, target_lightness=max(self._light.l, 0.8)
                        )
                    )
            else:
                self.variants.append(self._base)

        self._default = self._base

    def __getitem__(self, index):
        if index == 0:
            return self._base
        return self.variants[index - 1]

    @property
    def base(self):
        return self._base

    @property
    def default(self):
        return self._default

    @property
    def _1(self):
        return self.variants[0]

    @property
    def _2(self):
        return self.variants[1]

    @property
    def _3(self):
        return self.variants[2]

    @property
    def _4(self):
        return self.variants[3]

    @property
    def _5(self):
        return self.variants[4]

    @property
    def lightest(self):
        if self._scheme_type == SchemeType.LIGHT:
            return self.variants[4]
        return self.variants[0]

    @property
    def darkest(self):
        if self._scheme_type == SchemeType.DARK:
            return self.variants[4]
        return self.variants[0]

    def __str__(self):
        return self.to_string(format="css")

    def to_string(self, format="css", variant="base"):
        if variant == "base":
            return self._base.to_string(format)
        elif variant == "lightest":
            return self.lightest.to_string(format)
        elif variant == "darkest":
            return self.darkest.to_string(format)
        else:
            return self.variants[int(variant) - 1].to_string(format)

    @property
    def hex(self):
        return self.base.hex

    @property
    def css(self):
        return self.base.css

    def __hash__(self):
        return hash(self.base)

    def to_latex(self, name: str = None):
        if name is None:
            name = self._name
        if name is None:
            name = self._base.to_string("hex")
        out_string = []
        out_string.append(
            f"\\definecolor{{{name}}}{{HTML}}{{{self._base.to_string('hex')}}}"
        )
        for i in range(5):
            out_string.append(
                f"\\definecolor{{{name}_{i + 1}}}{{HTML}}{{{self.variants[i].to_string('hex')}}}"
            )
        return "\n".join(out_string)

    def to_css(self, name: str = None):
        if name is None:
            name = self._name
        if name is None:
            name = self._base.to_string("hex")
        if name.startswith("--"):
            name = name[2:]
        if (
            not name.startswith("clr")
            and not name.startswith("color")
            and not name.startswith("colour")
        ):
            name = f"clr-{name}"
        out_string = []
        out_string.append(f"--{name}: {self._base.to_string('css')};")
        for i in range(5):
            out_string.append(f"--{name}-{i + 1}: {self.variants[i].to_string('css')};")
        return "\n".join(out_string)

    def to_javascript(self, name: str = None):
        if name is None:
            name = self._name
        if name is None:
            name = self._base.to_string("hex")

        out_string = StringIO()
        out_string.write(f"{name}: {{\n")
        out_string.write(f"  base: '{self._base.to_string('css')}',\n")
        for i in range(5):
            out_string.write(f"  {i + 1}: '{self.variants[i].to_string('css')}',\n")
        out_string.write("}")
        return out_string.getvalue()


class ColorScheme:

    similarity_vals = {"light": {"s": 1, "l": 0.37}, "dark": {"s": 0.67, "l": 0.5}}

    saturation_threshold = {"light": 0.25, "dark": 0.25}

    def __init__(
        self,
        # colors: List[str] | List[Color],
        # foreground: str | Color = None,
        # background: str | Color = None,
        scheme: dict,
        scheme_type: SchemeType | str = SchemeType.LIGHT,
    ):
        # scheme dict must have the following properties:
        # - At least one of the following keys:
        #   - "colors": List[str] | List[Color]
        #   - "accents": List[str] | List[Color]
        # - optionally:
        #   - "surfaces": List[str] | List[Color]
        # - optionally, or required if "colors" is not specified:
        #   - "foreground": str | Color
        #   - "background": str | Color
        # - optionally as many or few of:
        #   - "red": str | Color
        #   - "orange": str | Color
        #   - "yellow": str | Color
        #   - "green": str | Color
        #   - "cyan": str | Color
        #   - "blue": str | Color
        #   - "purple": str | Color
        #   - "magenta": str | Color
        self._colors = None
        self._presets = {}
        self._distinct = None

        if isinstance(scheme_type, str):
            if scheme_type.lower() == "light":
                scheme_type = SchemeType.LIGHT
            elif scheme_type.lower() == "dark":
                scheme_type = SchemeType.DARK
            elif scheme_type.lower() == "empty":
                scheme_type = SchemeType.EMPTY

        if scheme_type == SchemeType.EMPTY:
            self._accents = None
            self._foreground = None
            self._background = None
            self._scheme_type = SchemeType.EMPTY
            self._surfaces = None
            return

        self._scheme_type = scheme_type
        self._accents = []
        self._surfaces = []

        # verify that the scheme has a valid structure:
        if (
            "colors" not in scheme
            or scheme["colors"] is None
            or len(scheme["colors"]) == 0
        ):
            if (
                "accents" not in scheme
                or scheme["accents"] is None
                or len(scheme["accents"]) == 0
            ):
                raise ValueError(
                    "Scheme must have at least one of the following keys: 'colors', 'accents', which cannot be empty."
                )
            if (
                "foreground" not in scheme
                or scheme["foreground"] is None
                or len(scheme["foreground"]) == 0
            ):  # string len, not list len
                raise ValueError(
                    "Without a 'colors' key, `scheme` must have a 'foreground' key, which cannot be empty."
                )
            if (
                "background" not in scheme
                or scheme["background"] is None
                or len(scheme["background"]) == 0
            ):
                raise ValueError(
                    "Without a 'colors' key, `scheme` must have a 'background' key, which cannot be empty."
                )

        if (
            "colors" in scheme
            and scheme["colors"] is not None
            and len(scheme["colors"]) > 0
        ):
            colors = [Color(c) if isinstance(c, str) else c for c in scheme["colors"]]
        else:
            colors = None

        if (
            "accents" in scheme
            and scheme["accents"] is not None
            and len(scheme["accents"]) > 0
        ):
            accents = [Color(c) if isinstance(c, str) else c for c in scheme["accents"]]
        else:
            accents = None

        if (
            "surfaces" in scheme
            and scheme["surfaces"] is not None
            and len(scheme["surfaces"]) > 0
        ):
            surfaces = [
                Color(c) if isinstance(c, str) else c for c in scheme["surfaces"]
            ]
        else:
            surfaces = None

        # start by getting foreground and background.
        if "foreground" in scheme and scheme["foreground"] is not None:
            foreground = Color(scheme["foreground"])
        else:
            if scheme_type == SchemeType.LIGHT:
                foreground = min(colors, key=lambda c: c.l)
            else:
                foreground = max(colors, key=lambda c: c.l)
            # remove foreground from colors
            colors.remove(foreground)

        if "background" in scheme and scheme["background"] is not None:
            background = Color(scheme["background"])
        else:
            if scheme_type == SchemeType.LIGHT:
                background = max(colors, key=lambda c: c.l)
            else:
                background = min(colors, key=lambda c: c.l)
            # remove background from colors
            colors.remove(background)

        # start by adding any accents to scheme._accents
        if accents is not None:
            self._accents.extend(accents)

        if surfaces is not None:
            self._surfaces.extend(surfaces)

        # now sort the remaining colors into the appropriate categories
        if colors is not None:
            for color in colors:
                if (
                    color.s_hsv
                    < ColorScheme.saturation_threshold[self._scheme_type.name.lower()]
                ):
                    self._surfaces.append(color)
                elif (
                    color.distance_to(foreground) < 10
                    or color.distance_to(background) < 10
                ):
                    self._surfaces.append(color)
                else:
                    self._accents.append(color)

        for i, color in enumerate(self._surfaces):
            self._surfaces[i] = ColorFamily(
                color, foreground, background, self._scheme_type
            )

        # sort surfaces. If the scheme is light, sort from lightest to darkest. If the scheme is dark, sort from darkest to lightest.
        self._surfaces.sort(
            key=lambda c: c.base.l, reverse=self._scheme_type == SchemeType.DARK
        )

        for i, color in enumerate(self._accents):
            self._accents[i] = ColorFamily(
                color, foreground, background, self._scheme_type
            )

        # Handle presets
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
            if name in scheme:
                c_hex = scheme[name]
                if isinstance(c_hex, str):
                    c_hex = Color(c_hex)
                i, c = self._get_internal_color_index(c_hex)
                if i is not None:
                    if c == "Accent":
                        self._presets[name] = self._accents[i]
                    elif c == "Surface":
                        self._presets[name] = self._surfaces[i]
                else:
                    # add to accents
                    self._accents.append(
                        ColorFamily(c_hex, foreground, background, self._scheme_type)
                    )
                    self._presets[name] = self._accents[-1]

        # TODO: set defaults for accents if the base is not appropriate

        # If we have fewer than 5 surface colours, generate more.
        if len(self.surfaces) <= 5:
            new_base = Color.from_hsl(
                (
                    background.h,
                    min(0.1, background.s),
                    background.l,
                )
            )
            new_base.lighten(0.1)
            new_surface_light = Color(background.hex if background.l > foreground.l else foreground.hex)
            new_surface_dark = Color(foreground.hex if background.l > foreground.l else background.hex)
            new_surface_light.l = min(1, new_surface_light.l + 0.05)
            new_surface_dark.l = max(0, new_surface_dark.l - 0.05)
            new_surfaces = ColorFamily(
                new_base, 
                light = new_surface_light,
                dark = new_surface_dark,
                scheme_type = self._scheme_type, 
                force_variants=True
            )

            for i in range(0, 6):
                if new_surfaces[i].h == 0 or new_surfaces[i].h == 360:
                    new_surfaces[i].h = new_base.h
            self._surfaces.extend(
                [
                    ColorFamily(
                        new_surfaces[i],
                        light = foreground,
                        dark = background,
                        scheme_type = self._scheme_type
                    )
                    for i in range(0, 6)
                ]
            )
            # sort the surfaces again
            self._surfaces.sort(
                key=lambda c: c.base.l, reverse=self._scheme_type == SchemeType.DARK
            )

        self._foreground = ColorFamily(
            foreground, foreground, background, self._scheme_type
        )
        self._background = ColorFamily(
            background, foreground, background, self._scheme_type
        )

    @property
    def accents(self):
        return self._accents

    @property
    def surfaces(self):
        return self._surfaces

    @property
    def foreground(self):
        return self._foreground

    @property
    def background(self):
        return self._background

    @property
    def colors(self):
        if self._colors is None:
            self._colors = (
                [self._foreground, self._background] + self._accents + self._surfaces
            )
        return self._colors

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.colors[index]
        elif isinstance(index, str):
            if index == "foreground":
                return self._foreground
            if index == "background":
                return self._background
            # go through each color, and if it has a name see if it matches (case insensitive)
            for color in self.colors:
                if color.name is not None and index.lower() == color.name.lower():
                    return color
            if index in [
                "red",
                "orange",
                "yellow",
                "green",
                "cyan",
                "blue",
                "purple",
                "magenta",
                "info",
                "success",
                "warning",
                "error",
            ]:
                return getattr(self, index)
            raise KeyError(f"Color with name '{index}' not found")
        else:
            raise TypeError(f"Invalid index type '{type(index)}'")

    def __iter__(self):
        return iter(self.colors)

    def get_closest_color(
        self, color: str | Color, accents_only: bool = False
    ) -> ColorFamily:
        if isinstance(color, str):
            color = Color(color)

        # use Color.distance_to() to find the closest color
        if accents_only:
            return min(self.accents, key=lambda c: c.base.distance_to(color))
        return min(self.colors, key=lambda c: c.base.distance_to(color))

    # hues:
    # * red: 0
    # * orange: 30
    # * yellow: 50
    # * green: 120
    # * cyan: 180
    # * blue: 240
    # * purple: 270
    # * magenta: 300

    @property
    def red(self):
        if "red" not in self._presets:
            self._presets["red"] = self.get_closest_color(
                Color.from_hsl(
                    (
                        0,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "s"
                        ],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "l"
                        ],
                    )
                ),
                accents_only=True,
            )
        return self._presets["red"]

    @property
    def orange(self):
        if "orange" not in self._presets:
            self._presets["orange"] = self.get_closest_color(
                Color.from_hsl(
                    (
                        30,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "s"
                        ],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "l"
                        ],
                    )
                ),
                accents_only=True,
            )
        return self._presets["orange"]

    @property
    def yellow(self):
        if "yellow" not in self._presets:
            self._presets["yellow"] = self.get_closest_color(
                Color.from_hsl(
                    (
                        50,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "s"
                        ],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "l"
                        ],
                    )
                ),
                accents_only=True,
            )
        return self._presets["yellow"]

    @property
    def green(self):
        if "green" not in self._presets:
            self._presets["green"] = self.get_closest_color(
                Color.from_hsl(
                    (
                        120,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "s"
                        ],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "l"
                        ],
                    )
                ),
                accents_only=True,
            )
        return self._presets["green"]

    @property
    def cyan(self):
        if "cyan" not in self._presets:
            self._presets["cyan"] = self.get_closest_color(
                Color.from_hsl(
                    (
                        180,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "s"
                        ],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "l"
                        ],
                    )
                ),
                accents_only=True,
            )
        return self._presets["cyan"]

    @property
    def blue(self):
        if "blue" not in self._presets:
            self._presets["blue"] = self.get_closest_color(
                Color.from_hsl(
                    (
                        220,  # Err towards cyan instead of purple
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "s"
                        ],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "l"
                        ],
                    )
                ),
                accents_only=True,
            )
        return self._presets["blue"]

    @property
    def purple(self):
        if "purple" not in self._presets:
            self._presets["purple"] = self.get_closest_color(
                Color.from_hsl(
                    (
                        270,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "s"
                        ],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "l"
                        ],
                    )
                ),
                accents_only=True,
            )
        return self._presets["purple"]

    @property
    def magenta(self):
        if "magenta" not in self._presets:
            self._presets["magenta"] = self.get_closest_color(
                Color.from_hsl(
                    (
                        300,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "s"
                        ],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower()][
                            "l"
                        ],
                    )
                ),
                accents_only=True,
            )
        return self._presets["magenta"]

    @property
    def info(self):
        return self.blue

    @property
    def success(self):
        return self.green

    @property
    def warning(self):
        if self.yellow == self.green:  # this can happen quite a lot
            # We might also have orange == red, but better to have warnings in red than in green, though
            return self.orange
        return self.yellow

    @property
    def error(self):
        return self.red

    @property
    def distinct(self):
        if self._distinct is None:
            # we need to work out an optimal set of colors such that no two colors are too similar
            # We'll only take colours from self._accents, as surfaces will be intentionally similar
            # we can do this by using a greedy algorithm
            # we'll start with the first color, and then add the next color that is the furthest away
            # from all the colors we've already added
            # we'll do this until we have only colors which are too close left

            distances = {}
            for color in self._accents:
                distances[color] = {}
                for color2 in self._accents:
                    distances[color][color2] = color.base.distance_to(color2.base)

            # we'll start with the first color
            distinct_colors = [self._accents[0]]

            while len(distinct_colors) < len(self._accents):
                # find the next color that is the furthest away from all the colors we've already added
                next_color = max(
                    self._accents,
                    key=lambda c: min(distances[c][d] for d in distinct_colors),
                )
                dist = min(distances[next_color][d] for d in distinct_colors)
                if dist < (
                    15 if len(self.accents) > 6 else 10
                ):  # be less strict if we have fewer colours to choose from
                    # the furthest color is too close to one of the colors we've already added
                    # This means all subsequent colors will be too close to one of the colors we've already added
                    # so we're finished
                    break
                distinct_colors.append(next_color)

            # reorder so that they are the in the same order as they appear in self._accents (should help to avoid red and green being next to each other so often)
            distinct_colors = [c for c in self._accents if c in distinct_colors]

            self._distinct = distinct_colors

        return self._distinct

    def _get_internal_color_index(self, color, css=False):
        if isinstance(color, Color):
            for i, c in enumerate(self._accents):
                if c.base == color:
                    if css:
                        return i, "accent"
                    return i, "Accent"
            for i, c in enumerate(self._surfaces):
                if c.base == color:
                    if css:
                        return i, "surface"
                    return i, "Surface"
            return None, None
        elif isinstance(color, ColorFamily):
            for i, c in enumerate(self._accents):
                if c == color:
                    if css:
                        return i, "accent"
                    return i, "Accent"
            for i, c in enumerate(self._surfaces):
                if c == color:
                    if css:
                        return i, "surface"
                    return i, "Surface"
            return None, None
        elif isinstance(color, str):
            for i, c in enumerate(self._accents):
                if (
                    hasattr(c, "name") and c.name == color
                ) or c.base.hex == color.replace("#", ""):
                    if css:
                        return i, "accent"
                    return i, "Accent"
            for i, c in enumerate(self._surfaces):
                if (
                    hasattr(c, "name") and c.name == color
                ) or c.base.hex == color.replace("#", ""):
                    if css:
                        return i, "surface"
                    return i, "Surface"
            return None, None

    def to_latex(self):
        out_string = []
        out_string += self.foreground.to_latex("ForegroundColour").splitlines()
        out_string += self.background.to_latex("BackgroundColour").splitlines()
        for i, color in enumerate(self.accents):
            out_string += color.to_latex(f"Accent{i+1}").splitlines()
        for i, color in enumerate(self.surfaces):
            out_string += color.to_latex(f"Surface{i+1}").splitlines()

        for c, name in zip(
            [
                self.red,
                self.orange,
                self.yellow,
                self.green,
                self.cyan,
                self.blue,
                self.purple,
                self.magenta,
            ],
            ["Red", "Orange", "Yellow", "Green", "Cyan", "Blue", "Purple", "Magenta"],
        ):
            i, t = self._get_internal_color_index(c)
            if i is None:
                raise ValueError(
                    f"Could not find color {c} in color scheme, even though it currently exists as self.{name.lower()}"
                )
            out_string += [
                f"\\colorlet{{{name.capitalize()}}}{{{t.capitalize()}{i+1}}}"
            ] + [
                f"\\colorlet{{{name.capitalize()}_{j+1}}}{{{t.capitalize()}{i+1}_{j+1}}}"
                for j in range(5)
            ]

        for c, name in zip(
            [self.info, self.success, self.warning, self.error],
            ["Info", "Success", "Warning", "Error"],
        ):
            i, t = self._get_internal_color_index(c)
            if i is None:
                raise ValueError(
                    f"Could not find color {c} in color scheme, even though it currently exists as self.{name.lower()}"
                )
            out_string += [
                f"\\colorlet{{{name.capitalize()}}}{{{t.capitalize()}{i+1}}}"
            ] + [
                f"\\colorlet{{{name.capitalize()}_{j+1}}}{{{t.capitalize()}{i+1}_{j+1}}}"
                for j in range(5)
            ]
        return "\n".join(out_string)

    @staticmethod
    def _empty():
        return ColorScheme({}, scheme_type=SchemeType.EMPTY)

    def to_css(self):
        out_string = []
        out_string += [":root {"]
        out_string += self.foreground.to_css("foreground").splitlines()
        out_string += self.background.to_css("background").splitlines()
        for i, color in enumerate(self.accents):
            out_string += color.to_css(f"accent{i+1}").splitlines()
        for i, color in enumerate(self.surfaces):
            out_string += color.to_css(f"surface{i+1}").splitlines()

        for c, name in zip(
            [
                self.red,
                self.orange,
                self.yellow,
                self.green,
                self.cyan,
                self.blue,
                self.purple,
                self.magenta,
            ],
            ["red", "orange", "yellow", "green", "cyan", "blue", "purple", "magenta"],
        ):
            i, t = self._get_internal_color_index(c, css=True)
            if i is None:
                raise ValueError(
                    f"Could not find color {c} in color scheme, even though it currently exists as self.{name.lower()}"
                )
            out_string += [f"--clr-{name}: var(--clr-{t}{i+1});"] + [
                f"--clr-{name}-{j+1}: var(--clr-{t}{i+1}-{j+1});" for j in range(5)
            ]

        for c, name in zip(
            [self.info, self.success, self.warning, self.error],
            ["info", "success", "warning", "error"],
        ):
            i, t = self._get_internal_color_index(c, css=True)
            if i is None:
                raise ValueError(
                    f"Could not find color {c} in color scheme, even though it currently exists as self.{name.lower()}"
                )
            out_string += [f"--clr-{name}: var(--clr-{t}{i+1});"] + [
                f"--clr-{name}-{j+1}: var(--clr-{t}{i+1}-{j+1});" for j in range(5)
            ]
        out_string += ["}"]
        return "\n".join(out_string)

    def to_javascript(self):
        # return the scheme as a json object
        out_string = StringIO()
        out_string.write("const colours = {\n")
        out_string.write(self.foreground.to_javascript("foreground") + ",\n")
        out_string.write(self.background.to_javascript("background") + ",\n")
        for i, color in enumerate(self.accents):
            out_string.write(color.to_javascript(f"accent{i+1}") + ",\n")
        for i, color in enumerate(self.surfaces):
            out_string.write(color.to_javascript(f"surface{i+1}") + ",\n")

        out_string.write("};\n")
        out_string.write("colours.accents = {\n")
        for i in range(len(self.accents)):
            out_string.write(f"  {i+1}: colours.accent{i+1},\n")
        out_string.write("};\n")
        out_string.write("colours.surfaces = {\n")
        for i in range(len(self.surfaces)):
            out_string.write(f"  {i+1}: colours.surface{i+1},\n")
        out_string.write("};\n")
        for c, name in zip(
            [
                self.red,
                self.orange,
                self.yellow,
                self.green,
                self.cyan,
                self.blue,
                self.purple,
                self.magenta,
            ],
            ["red", "orange", "yellow", "green", "cyan", "blue", "purple", "magenta"],
        ):
            i, t = self._get_internal_color_index(c, css=True)
            if i is None:
                raise ValueError(
                    f"Could not find color {c} in color scheme, even though it currently exists as self.{name.lower()}"
                )
            out_string.write(f"colours.{name} = colours.{t}{i+1};\n")
        return out_string.getvalue()

    def to_rich_swatch(self):
        from rich.text import Text

        text = Text()
        text += Text("\u2588\u2588", style=self.foreground.base.css)
        text += Text("\u2588\u2588", style=self.background.base.css)
        # for color in self.accents:
        #     text += Text("\u2588\u2588", style = color.base.css)
        # for color in self.surfaces:
        #     text += Text("\u2588\u2588", style = color.base.css)
        for color in [
            "red",
            "orange",
            "yellow",
            "green",
            "cyan",
            "blue",
            "purple",
            "magenta",
        ]:
            text += Text("\u2588\u2588", style=getattr(self, color).base.css)
        return text
