
# ToDo: 
# - Allow for colour dict to specify separate accent or surface colours, as well as specific colours to use as red, orange, etc. (without adding duplicate colours)
# - Amend ColorFamily to have a default, which will normally be base unless base is too similar to the light or dark color, in which case it will be a lighter or darker variant.
# - ColorScheme should take a dictionary instead of colors, foreground, background, etc. as separate arguments.

from typing import List
import math
import numpy as np

from enum import Enum

# We need to be careful with Enums because by default equality only works with the exact same enum. We want to be able to check with Enums *or* integers, especially in match/case blocks.


class EnumEx(Enum):
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


class RGB:
    def __init__(self, rgb: int | List[int], g: int = None, b: int = None):
        if isinstance(rgb, list) or isinstance(rgb, tuple):
            self.r = rgb[0]
            self.g = rgb[1]
            self.b = rgb[2]
        else:
            self.r = rgb
            self.g = g
            self.b = b

    def __repr__(self):
        return f'RGB({self.r}, {self.g}, {self.b})'

    def __str__(self):
        return f'RGB({self.r}, {self.g}, {self.b})'

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b

    # iterator compatibility
    def __iter__(self):
        return iter((self.r, self.g, self.b))


class HSL:
    def __init__(self, hsl: int | List[int], s: int = None, l: int = None):
        if isinstance(hsl, list) or isinstance(hsl, tuple):
            self.h = hsl[0]
            self.s = hsl[1]
            self.l = hsl[2]
        else:
            self.h = hsl
            self.s = s
            self.l = l

    def __repr__(self):
        return f'HSL({self.h}, {self.s}, {self.l})'

    def __str__(self):
        return f'HSL({self.h}, {self.s}, {self.l})'

    def __eq__(self, other):
        return self.h == other.h and self.s == other.s and self.l == other.l

    def __iter__(self):
        return iter((self.h, self.s, self.l))


class HSV:
    def __init__(self, hsv: int | List[int], s: int = None, v: int = None):
        if isinstance(hsv, list) or isinstance(hsv, tuple):
            self.h = hsv[0]
            self.s = hsv[1]
            self.v = hsv[2]
        else:
            self.h = hsv
            self.s = s
            self.v = v

    def __repr__(self):
        return f'HSV({self.h}, {self.s}, {self.v})'

    def __str__(self):
        return f'HSV({self.h}, {self.s}, {self.v})'

    def __eq__(self, other):
        return self.h == other.h and self.s == other.s and self.v == other.v

    def __iter__(self):
        return iter((self.h, self.s, self.v))


class XYZ:
    def __init__(self, xyz: int | List[int], y: int = None, z: int = None):
        if isinstance(xyz, list) or isinstance(xyz, tuple):
            self.x = xyz[0]
            self.y = xyz[1]
            self.z = xyz[2]
        else:
            self.x = xyz
            self.y = y
            self.z = z

    def __repr__(self):
        return f'XYZ({self.x}, {self.y}, {self.z})'

    def __str__(self):
        return f'XYZ({self.x}, {self.y}, {self.z})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __iter__(self):
        return iter((self.x, self.y, self.z))


class LAB:
    def __init__(self, lab: int | List[int], a: int = None, b: int = None):
        if isinstance(lab, list) or isinstance(lab, tuple):
            self.l = lab[0]
            self.a = lab[1]
            self.b = lab[2]
        else:
            self.l = lab
            self.a = a
            self.b = b

    def __repr__(self):
        return f'LAB({self.l}, {self.a}, {self.b})'

    def __str__(self):
        return f'LAB({self.l}, {self.a}, {self.b})'

    def __eq__(self, other):
        return self.l == other.l and self.a == other.a and self.b == other.b

    def __iter__(self):
        return iter((self.l, self.a, self.b))


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
        if hex[0] == '#':
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

    # Converters
    # - hex to rgb
    # - rgb to hex
    # - rgb to hsl
    # - hsl to rgb
    # - rgb to hsv
    # - hsv to rgb
    # - rgb to xyz
    # - xyz to rgb
    # - rgb to lab
    # - lab to rgb
    @staticmethod
    def hex_to_rgb(hex: str) -> RGB:
        return RGB(tuple(int(hex[i:i+2], 16) for i in (0, 2, 4)))

    @staticmethod
    def rgb_to_hex(rgb: tuple | RGB) -> str:
        return ''.join(f'{x:02x}' for x in rgb)

    @staticmethod
    def rgb_to_hsl(rgb: tuple | RGB) -> HSL:
        r, g, b = (x / 255 for x in rgb)
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
        return HSL(h, s, l)

    @staticmethod
    def hsl_to_rgb(hsl: tuple | HSL) -> RGB:
        h, s, l = hsl
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return RGB(tuple(int(255 * (x + m)) for x in (r, g, b)))

    @staticmethod
    def rgb_to_hsv(rgb: tuple | RGB) -> HSV:
        r, g, b = (x / 255 for x in rgb)
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
        return HSV(h, s, v)

    @staticmethod
    def hsv_to_rgb(hsv: tuple | HSV) -> RGB:
        h, s, v = hsv
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return RGB(tuple(int(255 * (x + m)) for x in (r, g, b)))

    @staticmethod
    def rgb_to_xyz(rgb: tuple | RGB) -> XYZ:
        r, g, b = (x / 255 for x in rgb)
        r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
        x = r * 0.4124 + g * 0.3576 + b * 0.1805
        y = r * 0.2126 + g * 0.7152 + b * 0.0722
        z = r * 0.0193 + g * 0.1192 + b * 0.9505
        return XYZ(x * 100, y * 100, z * 100)

    @staticmethod
    def xyz_to_rgb(xyz: tuple | XYZ) -> RGB:
        x, y, z = (x / 100 for x in xyz)
        r = x * 3.2406 + y * -1.5372 + z * -0.4986
        g = x * -0.9689 + y * 1.8758 + z * 0.0415
        b = x * 0.0557 + y * -0.2040 + z * 1.0570
        r = 12.92 * r if r <= 0.0031308 else (1.055 * r ** (1 / 2.4)) - 0.055
        g = 12.92 * g if g <= 0.0031308 else (1.055 * g ** (1 / 2.4)) - 0.055
        b = 12.92 * b if b <= 0.0031308 else (1.055 * b ** (1 / 2.4)) - 0.055
        return RGB(tuple(int(255 * x) for x in (r, g, b)))

    @staticmethod
    def rgb_to_lab(rgb: tuple | RGB) -> LAB:
        x, y, z = Color.rgb_to_xyz(rgb)
        x /= 95.047
        y /= 100.000
        z /= 108.883
        x = x ** (1 / 3) if x > 0.008856 else (7.787 * x) + (16 / 116)
        y = y ** (1 / 3) if y > 0.008856 else (7.787 * y) + (16 / 116)
        z = z ** (1 / 3) if z > 0.008856 else (7.787 * z) + (16 / 116)
        l = (116 * y) - 16
        a = 500 * (x - y)
        b = 200 * (y - z)
        return LAB(l, a, b)

    @staticmethod
    def lab_to_rgb(lab: tuple | LAB) -> RGB:
        l, a, b = lab
        y = (l + 16) / 116
        x = a / 500 + y
        z = y - b / 200
        x = x ** 3 if x > 0.206893 else (x - 16 / 116) / 7.787
        y = y ** 3 if y > 0.206893 else (y - 16 / 116) / 7.787
        z = z ** 3 if z > 0.206893 else (z - 16 / 116) / 7.787
        x *= 95.047
        y *= 100.000
        z *= 108.883
        return Color.xyz_to_rgb((x, y, z))

    @staticmethod
    def from_hsl(hsl: tuple | HSL):
        return Color(Color.rgb_to_hex(Color.hsl_to_rgb(hsl)))

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
            self._rgb = Color.hex_to_rgb(self.hex)
        return self._rgb

    @rgb.setter
    def rgb(self, value: tuple):
        self._hex = Color.rgb_to_hex(value)
        self.clear_cache()

    @property
    def hsl(self) -> tuple:
        if self._hsl is None:
            self._hsl = Color.rgb_to_hsl(self.rgb)
        return self._hsl

    @hsl.setter
    def hsl(self, value: tuple):
        self._hex = Color.rgb_to_hex(Color.hsl_to_rgb(value))
        self.clear_cache()

    @property
    def hsv(self) -> tuple:
        if self._hsv is None:
            self._hsv = Color.rgb_to_hsv(self.rgb)
        return self._hsv

    @hsv.setter
    def hsv(self, value: tuple):
        self._hex = Color.rgb_to_hex(Color.hsv_to_rgb(value))
        self.clear_cache()

    @property
    def xyz(self) -> tuple:
        if self._xyz is None:
            self._xyz = Color.rgb_to_xyz(self.rgb)
        return self._xyz

    @xyz.setter
    def xyz(self, value: tuple):
        self._hex = Color.rgb_to_hex(Color.xyz_to_rgb(value))
        self.clear_cache()

    @property
    def lab(self) -> tuple:
        if self._lab is None:
            self._lab = Color.rgb_to_lab(self.rgb)
        return self._lab

    @lab.setter
    def lab(self, value: tuple):
        self._hex = Color.rgb_to_hex(Color.lab_to_rgb(value))
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

    def lighten(self, amount: float, in_place: bool = False):
        if amount > 1:
            amount /= 100
        new_l = 1 - (1 - self.hsl.l) * (1 - amount)
        if in_place:
            self.hsl = HSL(self.hsl.h, self.hsl.s, new_l)
        else:
            return Color(Color.rgb_to_hex(Color.hsl_to_rgb(HSL(self.hsl.h, self.hsl.s, new_l))))

    def darken(self, amount: float, in_place: bool = False):
        if amount > 1:
            amount /= 100
        new_l = self.hsl.l * (1 - amount)
        if in_place:
            self.hsl = HSL(self.hsl.h, self.hsl.s, new_l)
        else:
            return Color(Color.rgb_to_hex(Color.hsl_to_rgb(HSL(self.hsl.h, self.hsl.s, new_l))))

    def hue_diff(self, other):
        # Return the signed difference in hue between self and other, in degrees, accounting for wrapping at 360
        return (other.hsl.h - self.hsl.h + 180) % 360 - 180

    def move_to_color(self, other, amount: float, in_place: bool = False):
        # Move self towards other by amount, in place or not, in hsl space
        if amount > 1:
            amount /= 100
        new_h = self.hsl.h + self.hue_diff(other) * amount
        new_s = self.hsl.s + (other.hsl.s - self.hsl.s) * amount
        new_l = self.hsl.l + (other.hsl.l - self.hsl.l) * amount
        if in_place:
            self.hsl = HSL(new_h, new_s, new_l)
        else:
            return Color(Color.rgb_to_hex(Color.hsl_to_rgb(HSL(new_h, new_s, new_l))))

    def __str__(self):
        return self.to_string(format="hex-hash")

    def to_string(self, format="hex-hash"):
        if format == "hex-hash":
            return f"#{self.hex}"
        if format == "hex":
            return self.hex
        if format == "rgb":
            return f"rgb({self.r}, {self.g}, {self.b})"
        if format == "hsl":
            deg = "\u00b0"
            return f"hsl({self.h:.0f}{deg}, {self.s * 100:.0f}%, {self.l * 100:.0f}%)"
        if format == "hsv":
            deg = "\u00b0"
            return f"hsv({self.h:.0f}{deg}, {self.s * 100:.0f}%, {self.v * 100:.0f}%)"
        if format == "xyz":
            return f"xyz({self.x}, {self.y}, {self.z})"
        if format == "lab":
            return f"lab({self.l_lab}, {self.a_lab}, {self.b_lab})"
        return f"#{self.hex}"

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
        c1 = math.sqrt(a1 ** 2 + b1 ** 2)
        c2 = math.sqrt(a2 ** 2 + b2 ** 2)
        avgC = (c1 + c2) / 2
        g = (1 - math.sqrt(avgC ** 7 / (avgC ** 7 + 25 ** 7))) / 2

        a1p = a1 * (1 + g)
        a2p = a2 * (1 + g)

        c1p = math.sqrt(a1p ** 2 + b1 ** 2)
        c2p = math.sqrt(a2p ** 2 + b2 ** 2)

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

        t = 1 - 0.17 * math.cos(deg_to_rad(avgHp - 30)) + \
            0.24 * math.cos(deg_to_rad(2 * avgHp)) + \
            0.32 * math.cos(deg_to_rad(3 * avgHp + 6)) - \
            0.2 * math.cos(deg_to_rad(4 * avgHp - 63))

        deltaHp = h2p - h1p
        if abs(deltaHp) > 180:
            if h2p <= h1p:
                deltaHp += 360
            else:
                deltaHp -= 360

        deltaLp = l2 - l1
        deltaCp = c2p - c1p
        deltaHp = 2 * math.sqrt(c1p * c2p) * math.sin(deg_to_rad(deltaHp) / 2)

        sL = 1 + ((0.015 * (avgL - 50) ** 2) /
                  math.sqrt(20 + (avgL - 50) ** 2))
        sC = 1 + 0.045 * avgCp
        sH = 1 + 0.015 * avgCp * t

        deltaRho = 30 * math.exp(-((avgHp - 275) / 25) ** 2)
        rc = 2 * math.sqrt((avgCp ** 7) / (avgCp ** 7 + 25 ** 7))
        rt = -rc * math.sin(2 * deg_to_rad(deltaRho))

        kl = 1
        kc = 1
        kh = 1

        deltaE = math.sqrt(
            (deltaLp / (kl * sL)) ** 2 +
            (deltaCp / (kc * sC)) ** 2 +
            (deltaHp / (kh * sH)) ** 2 +
            rt * (deltaCp / (kc * sC)) * (deltaHp / (kh * sH))
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
        name=None
    ):
        if isinstance(base, str):
            base = Color(base)
        if light is not None:
            if isinstance(light, str):
                light = Color(light)
        if dark is not None:
            if isinstance(dark, str):
                dark = Color(dark)
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

        too_light = (not use_light and self._base.l > 0.8) or (
            use_light and self._base.l / self._light.l > 0.95)
        too_dark = (not use_dark and self._base.l < 0.2) or (
            use_dark and self._dark.l / self._base.l > 0.95)

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
                    self.variants.append(
                        self._base.move_to_color(self._dark, -amount))
                else:
                    self.variants.append(self._base.darken(-amount))
            elif amount > 0:
                if use_light:
                    self.variants.append(
                        self._base.move_to_color(self._light, amount))
                else:
                    self.variants.append(self._base.lighten(amount))
            else:
                self.variants.append(self._base)

    def __getitem__(self, index):
        if index == 0:
            return self._base
        return self.variants[index - 1]

    @property
    def base(self):
        return self._base

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
        return self.to_string(format="hex-hash")

    def to_string(self, format="hex-hash", variant="base"):
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
            f"\\definecolor{{{name}}}{{HTML}}{{{self._base.to_string('hex')}}}")
        for i in range(5):
            out_string.append(
                f"\\definecolor{{{name}_{i + 1}}}{{HTML}}{{{self.variants[i].to_string('hex')}}}")
        return "\n".join(out_string)


class ColorScheme:

    similarity_vals = {
        "light": {
            "s": 1,
            "l": 0.37
        },
        "dark": {
            "s": 0.67,
            "l": 0.5
        }
    }

    saturation_threshold = {
        "light": 0.25,
        "dark": 0.25
    }

    def __init__(
        self,
        colors: List[str] | List[Color],
        foreground: str | Color = None,
        background: str | Color = None,
        scheme_type: SchemeType | str = SchemeType.LIGHT
    ):
        self._colors = None
        self._red = None
        self._orange = None
        self._yellow = None
        self._green = None
        self._blue = None
        self._purple = None
        self._cyan = None
        self._magenta = None
        self._distinct = None

        if scheme_type == SchemeType.EMPTY:
            self._accents = None
            self._foreground = None
            self._background = None
            self._scheme_type = SchemeType.EMPTY
            self._surfaces = None
            return

        # convert all colors to Color objects if they're not already
        for i in range(len(colors)):
            if isinstance(colors[i], str):
                colors[i] = Color(colors[i])

        if foreground is not None:
            if isinstance(foreground, str):
                foreground = Color(foreground)
        else:
            if scheme_type == SchemeType.LIGHT:
                # find the darkest color
                foreground = min(colors, key=lambda c: c.l)
            else:
                # find the lightest color
                foreground = max(colors, key=lambda c: c.l)

        if background is not None:
            if isinstance(background, str):
                background = Color(background)
        else:
            if scheme_type == SchemeType.LIGHT:
                # find the lightest color
                background = max(colors, key=lambda c: c.l)
            else:
                # find the darkest color
                background = min(colors, key=lambda c: c.l)

        if isinstance(scheme_type, str):
            if scheme_type.lower() == "light":
                scheme_type = SchemeType.LIGHT
            elif scheme_type.lower() == "dark":
                scheme_type = SchemeType.DARK
            else:
                raise ValueError(f"Invalid scheme type '{scheme_type}'")

        self._scheme_type = scheme_type

        self._accents = []
        self._surfaces = []

        for color in colors:
            if color.s_hsv < ColorScheme.saturation_threshold[self._scheme_type.name.lower()]:
                self._surfaces.append(
                    ColorFamily(
                        color,
                        foreground,
                        background,
                        self._scheme_type
                    )
                )
            elif color.distance_to(foreground) < 10 or color.distance_to(background) < 10:
                self._surfaces.append(
                    ColorFamily(
                        color,
                        foreground,
                        background,
                        self._scheme_type
                    )
                )
            else:
                self._accents.append(
                    ColorFamily(
                        color,
                        foreground,
                        background,
                        self._scheme_type
                    )
                )

        # sort surfaces. If the scheme is light, sort from lightest to darkest. If the scheme is dark, sort from darkest to lightest.
        self._surfaces.sort(key=lambda c: c.base.l,
                            reverse=self._scheme_type == SchemeType.DARK)

        self._foreground = ColorFamily(
            foreground,
            foreground,
            background,
            self._scheme_type
        )
        self._background = ColorFamily(
            background,
            foreground,
            background,
            self._scheme_type
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
            self._colors = [self._foreground, self._background] + \
                self._accents + self._surfaces
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
            raise KeyError(f"Color with name '{index}' not found")
        else:
            raise TypeError(f"Invalid index type '{type(index)}'")

    def __iter__(self):
        return iter(self.colors)

    def get_closest_color(self, color: str | Color, accents_only: bool = False) -> ColorFamily:
        if isinstance(color, str):
            color = Color(color)

        # use Color.distance_to() to find the closest color
        if accents_only:
            return min(self.accents, key=lambda c: c.base.distance_to(color))
        return min(self.colors, key=lambda c: c.base.distance_to(color))

    # hues:
    # * red: 0
    # * orange: 30
    # * yellow: 60
    # * green: 120
    # * cyan: 180
    # * blue: 240
    # * purple: 270
    # * magenta: 300

    @property
    def red(self):
        if self._red is None:
            self._red = self.get_closest_color(
                Color.from_hsl(
                    (
                        0,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["s"],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["l"]
                    )
                ),
                accents_only=True
            )
        return self._red

    @property
    def orange(self):
        if self._orange is None:
            self._orange = self.get_closest_color(
                Color.from_hsl(
                    (
                        30,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["s"],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["l"]
                    )
                ),
                accents_only=True
            )
        return self._orange

    @property
    def yellow(self):
        if self._yellow is None:
            self._yellow = self.get_closest_color(
                Color.from_hsl(
                    (
                        60,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["s"],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["l"]
                    )
                ),
                accents_only=True
            )
        return self._yellow

    @property
    def green(self):
        if self._green is None:
            self._green = self.get_closest_color(
                Color.from_hsl(
                    (
                        120,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["s"],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["l"]
                    )
                ),
                accents_only=True
            )
        return self._green

    @property
    def cyan(self):
        if self._cyan is None:
            self._cyan = self.get_closest_color(
                Color.from_hsl(
                    (
                        180,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["s"],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["l"]
                    )
                ),
                accents_only=True
            )
        return self._cyan

    @property
    def blue(self):
        if self._blue is None:
            self._blue = self.get_closest_color(
                Color.from_hsl(
                    (
                        220, # Err towards cyan instead of purple
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["s"],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["l"]
                    )
                ),
                accents_only=True
            )
        return self._blue

    @property
    def purple(self):
        if self._purple is None:
            self._purple = self.get_closest_color(
                Color.from_hsl(
                    (
                        270,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["s"],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["l"]
                    )
                ),
                accents_only=True
            )
        return self._purple

    @property
    def magenta(self):
        if self._magenta is None:
            self._magenta = self.get_closest_color(
                Color.from_hsl(
                    (
                        300,
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["s"],
                        ColorScheme.similarity_vals[self._scheme_type.name.lower(
                        )]["l"]
                    )
                ),
                accents_only=True
            )
        return self._magenta

    @property
    def info(self):
        return self.blue

    @property
    def success(self):
        return self.green

    @property
    def warning(self):
        if self.yellow == self.green: # this can happen quite a lot
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
                    distances[color][color2] = color.base.distance_to(
                        color2.base)

            # we'll start with the first color
            distinct_colors = [self._accents[0]]

            while len(distinct_colors) < len(self._accents):
                # find the next color that is the furthest away from all the colors we've already added
                next_color = max(self._accents, key=lambda c: min(
                    distances[c][d] for d in distinct_colors))
                dist = min(distances[next_color][d] for d in distinct_colors)
                if dist < (15 if len(self.accents) > 6 else 10): # be less strict if we have fewer colours to choose from
                    # the furthest color is too close to one of the colors we've already added
                    # This means all subsequent colors will be too close to one of the colors we've already added
                    # so we're finished
                    break
                distinct_colors.append(next_color)

            # reorder so that they are the in the same order as they appear in self._accents (should help to avoid red and green being next to each other so often)
            distinct_colors = [
                c for c in self._accents if c in distinct_colors]

            self._distinct = distinct_colors

        return self._distinct

    def _get_internal_color_index(self, color):
        if isinstance(color, Color):
            for i, c in enumerate(self._accents):
                if c.base == color:
                    return i, "Accent"
            for i, c in enumerate(self._surfaces):
                if c.base == color:
                    return i, "Surface"
            return None, None
        elif isinstance(color, ColorFamily):
            for i, c in enumerate(self._accents):
                if c == color:
                    return i, "Accent"
            for i, c in enumerate(self._surfaces):
                if c == color:
                    return i, "Surface"
            return None, None
        elif isinstance(color, str):
            for i, c in enumerate(self._accents):
                if c.name == color or c.base.hex == color.replace("#", ""):
                    return i, "Accent"
            for i, c in enumerate(self._surfaces):
                if c.name == color or c.base.hex == color.replace("#", ""):
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
            [self.red, self.orange, self.yellow, self.green,
                self.cyan, self.blue, self.purple, self.magenta],
            ["Red", "Orange", "Yellow", "Green",
                "Cyan", "Blue", "Purple", "Magenta"]
        ):
            i, t = self._get_internal_color_index(c)
            if i is None:
                raise ValueError(
                    f"Could not find color {c} in color scheme, even though it currently exists as self.{name.lower()}")
            out_string += [
                f"\\colorlet{{{name.capitalize()}}}{{{t.capitalize()}{i+1}}}"
            ] + [
                f"\\colorlet{{{name.capitalize()}_{j+1}}}{{{t.capitalize()}{i+1}_{j+1}}}" for j in range(5)
            ]

        for c, name in zip([self.info, self.success, self.warning, self.error], ["Info", "Success", "Warning", "Error"]):
            i, t = self._get_internal_color_index(c)
            if i is None:
                raise ValueError(
                    f"Could not find color {c} in color scheme, even though it currently exists as self.{name.lower()}")
            out_string += [
                f"\\colorlet{{{name.capitalize()}}}{{{t.capitalize()}{i+1}}}"
            ] + [
                f"\\colorlet{{{name.capitalize()}_{j+1}}}{{{t.capitalize()}{i+1}_{j+1}}}" for j in range(5)
            ]
        return "\n".join(out_string)

    @staticmethod
    def _empty():
        return ColorScheme(
            [],
            "#000000",
            "#FFFFFF",
            scheme_type=SchemeType.EMPTY
        )
