from abc import ABC, abstractmethod
from enum import IntEnum
from typing import ClassVar, Final
import math
from dataclasses import dataclass, InitVar, fields


class ColorModel(ABC):
    BOUNDS: tuple[tuple[float | None, float | None], ...] = ()

    @abstractmethod
    def _normalize(self):
        # To allow for things like hue wrapping before bounds are checked.
        pass

    def __post_init__(self):

        self._normalize()

        if self.clamp:
            for field, (low, high) in zip(fields(self), self.BOUNDS):
                val = getattr(self, field.name)
                object.__setattr__(self, field.name, min(high, max(low, val)))
        else:
            for field, (low, high) in zip(fields(self), self.BOUNDS):
                val = getattr(self, field.name)
                if low is not None and val < low:
                    raise ValueError(f"Value {val} is below minimum {low}")
                if high is not None and val > high:
                    raise ValueError(f"Value {val} is above maximum {high}")

    @abstractmethod
    def to_full_rgb(self) -> tuple[float]:
        # This should return a tuple of 3 floats [0,1], not ints, to maintain as much precision as possible
        pass

    @abstractmethod
    def from_full_rgb(rgb: tuple[float]):
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


@dataclass(frozen = True, slots = True)
class RGB(ColorModel):
    r: int
    g: int
    b: int
    clamp: InitVar[bool] = False
    BOUNDS: ClassVar[Final] = ((0, 255), (0, 255), (0, 255))

    def to_full_rgb(self) -> tuple[float, float, float]:
        return (self.r / 255, self.g / 255, self.b / 255)

    @classmethod
    def from_full_rgb(cls, rgb: tuple[float, float, float]):
        return cls(map(lambda x: int(round(x * 255)), rgb))

    @classmethod
    def from_hex(cls, hex: str):
        return cls(tuple(int(hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)))

@dataclass(frozen = True, slots = True)
class HSL(ColorModel):
    h: float
    s: float
    l: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, 360), (0, 1), (0, 1))

    def _normalize(self):
        object.__setattr__(self, "h", float(self.h % 360))

    def to_full_rgb(self) -> tuple[float, float, float]:
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
    def from_full_rgb(cls, rgb: tuple[float]):
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
        return cls(h, s, l)


@dataclass(frozen = True, slots = True)
class HSV(ColorModel):
    h: float
    s: float
    v: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, 360), (0, 1), (0, 1))

    def _normalize(self):
        object.__setattr__(self, "h", float(self.h % 360))

    def to_full_rgb(self) -> tuple[float, float, float]:
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
    def from_full_rgb(cls, rgb: tuple[float]):
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
        return cls(h, s, v)

@dataclass(frozen = True, slots = True)
class XYZ(ColorModel):
    x: float
    y: float
    z: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, None), (0, None), (0, None))

    def to_full_rgb(self) -> tuple[float]:
        x, y, z = (x / 100 for x in (self.x, self.y, self.z))
        r = x * 3.2406 + y * -1.5372 + z * -0.4986
        g = x * -0.9689 + y * 1.8758 + z * 0.0415
        b = x * 0.0557 + y * -0.2040 + z * 1.0570
        r = 12.92 * r if r <= 0.0031308 else (1.055 * r ** (1 / 2.4)) - 0.055
        g = 12.92 * g if g <= 0.0031308 else (1.055 * g ** (1 / 2.4)) - 0.055
        b = 12.92 * b if b <= 0.0031308 else (1.055 * b ** (1 / 2.4)) - 0.055
        return (r, g, b)

    @classmethod
    def from_full_rgb(cls, rgb: tuple[float]):
        r, g, b = (
            x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb
        )
        x = r * 0.4124 + g * 0.3576 + b * 0.1805
        y = r * 0.2126 + g * 0.7152 + b * 0.0722
        z = r * 0.0193 + g * 0.1192 + b * 0.9505
        return cls(x * 100, y * 100, z * 100)

@dataclass(frozen = True, slots = True)
class LAB(ColorModel):
    l: float
    a: float
    b: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, None), (None, None), (None, None))

    def _to_xyz(self) -> XYZ:
        # https://en.wikipedia.org/wiki/CIELAB_color_space
        def f(t):
            if t > 6 / 29:
                return t**3
            return (t - 4 / 29) / 7.787

        y = (self.L + 16) / 116
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
        return cls(116 * y - 16, 500 * (x - y), 200 * (y - z))

    
    def to_full_rgb(self) -> tuple[float, float, float]:
        # lab to rgb, using xyz as an intermediate step
        return self._to_xyz().to_full_rgb()

    @classmethod
    def from_full_rgb(cls, rgb: tuple[float, float, float]):
        # rgb to lab, using xyz as an intermediate step
        return cls._from_xyz(XYZ.from_full_rgb(rgb))
