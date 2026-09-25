from abc import ABC, abstractmethod
from enum import IntEnum
from typing import ClassVar, Final
import math
from dataclasses import dataclass, InitVar, fields


class ColorModel(ABC):
    BOUNDS: tuple[tuple[float | None, float | None], ...] = ()

    def _normalize(self):
        # To allow for things like hue wrapping before bounds are checked.
        pass

    def __post_init__(self, clamp: bool = False):

        self._normalize()

        if clamp:
            for field, (low, high) in zip(fields(self), self.BOUNDS):
                val = getattr(self, field.name)
                if low is not None and val < low:
                    val = low
                if high is not None and val > high:
                    val = high
                object.__setattr__(self, field.name, val)
        else:
            for field, (low, high) in zip(fields(self), self.BOUNDS):
                val = getattr(self, field.name)
                if low is not None and val < low:
                    raise ValueError(f"Value {val} is below minimum {low}")
                if high is not None and val > high:
                    raise ValueError(f"Value {val} is above maximum {high}")

    def __iter__(self):
        for f in fields(self):
            yield getattr(self, f.name)

    def __getitem__(self, index: int) -> float | int:
        return self.as_tuple()[index]

    def __len__(self) -> int:
        # We could maybe return a fixed 3, but it's possible we could expand to include rgba or cymk at some point
        return len(self.as_tuple())

    @property
    def _a(self) -> float:
        return self[0]
    
    @property
    def _b(self) -> float:
        return self[1]

    @property
    def _c(self) -> float:
        return self[2]


    @abstractmethod
    def to_full_rgb(self) -> tuple[float]:
        # This should return a tuple of 3 floats [0,1], not ints, to maintain as much precision as possible
        pass

    @abstractmethod
    def from_full_rgb(rgb: tuple[float]):
        # This should take a tuple of 3 floats [0,1], not ints, to maintain as much precision as possible
        pass

    @staticmethod
    def _check_rgb_args(rgb: tuple[float] | tuple[tuple[float]]) -> tuple[float]:
        if len(rgb) == 1 and isinstance(rgb[0], (tuple, list)):
            rgb = rgb[0]
        if not len(rgb) == 3:
            raise ValueError(f"Expected 3 rgb values, but received {len(rgb)}")
        return rgb

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
                # If possible, avoid translating via rgb for these colour spaces with wider gamut
                if isinstance(self, LAB):
                    return self._to_xyz()
                if isinstance(self, OKLAB):
                    return self._to_xyz()
                if isinstance(self, OKLCH):
                    return self._to_oklab()._to_xyz()
                return XYZ.from_full_rgb(self.to_full_rgb())
            if new_model == "lab":
                if isinstance(self, XYZ):
                    return LAB._from_xyz(self)
                if isinstance(self, OKLAB):
                    return LAB._from_xyz(self._to_xyz())
                if isinstance(self, OKLCH):
                    return LAB._from_xyz(self._to_oklab()._to_xyz())
                return LAB.from_full_rgb(self.to_full_rgb())
            if new_model == "oklab":
                if isinstance(self, XYZ):
                    return OKLAB._from_xyz(self)
                if isinstance(self, LAB):
                    return OKLAB._from_xyz(self._to_xyz())
                if isinstance(self, OKLCH):
                    return self._to_oklab()
                return OKLAB.from_full_rgb(self.to_full_rgb())
            if new_model == "oklch":
                if isinstance(self, XYZ):
                    return OKLCH._from_oklab(OKLAB._from_xyz(self))
                if isinstance(self, LAB):
                    return OKLCH._from_oklab(OKLAB._from_xyz(self._to_xyz()))
                if isinstance(self, OKLAB):
                    return OKLCH._from_oklab(self)
                return OKLCH.from_full_rgb(self.to_full_rgb())
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
        return tuple(self)

    def _with_a(self, val: float) -> ColorModel:
        return self.__class__(val, self._b, self._c)

    def _with_b(self, val: float) -> ColorModel:
        return self.__class__(self._a, val, self._c)
    
    def _with_c(self, val: float) -> ColorModel:
        return self.__class__(self._a, self._b, val)

@dataclass(frozen = True, slots = True)
class RGB(ColorModel):
    r: int
    g: int
    b: int
    clamp: InitVar[bool] = False
    BOUNDS: ClassVar[Final] = ((0, 255), (0, 255), (0, 255))

    def _normalize(self):
        object.__setattr__(self, "r", int(round(self.r)))
        object.__setattr__(self, "g", int(round(self.g)))
        object.__setattr__(self, "b", int(round(self.b)))

    def to_full_rgb(self) -> tuple[float, float, float]:
        return (self.r / 255, self.g / 255, self.b / 255)

    @classmethod
    def from_full_rgb(cls, *rgb: tuple[float, float, float]):
        rgb = cls._check_rgb_args(rgb)
        return cls(*(min(255, max(0, int(round(x * 255)))) for x in rgb))

    @classmethod
    def from_hex(cls, hex: str):
        return cls(*(int(hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)))

    def to_hex(self) -> str:
        return f"{self.r:0>2X}{self.g:0>2X}{self.b:0>2X}"

    def with_r(self, val) -> RGB:
        return self._with_a(val)
    
    def with_g(self, val) -> RGB:
        return self._with_b(val)
    
    def with_b(self, val) -> RGB:
        return self._with_c(val)

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
    def from_full_rgb(cls, *rgb: tuple[float]):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        rgb = cls._check_rgb_args(rgb)
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

    def with_h(self, val) -> RGB:
        return self._with_a(val)
    
    def with_s(self, val) -> RGB:
        return self._with_b(val)
    
    def with_l(self, val) -> RGB:
        return self._with_c(val)



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
    def from_full_rgb(cls, *rgb: tuple[float]):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        rgb = cls._check_rgb_args(rgb)
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

    
    def with_h(self, val) -> RGB:
        return self._with_a(val)
    
    def with_s(self, val) -> RGB:
        return self._with_b(val)
    
    def with_v(self, val) -> RGB:
        return self._with_c(val)

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
    def from_full_rgb(cls, *rgb: tuple[float]):
        rgb = cls._check_rgb_args(rgb)
        r, g, b = (
            x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb
        )
        x = r * 0.4124 + g * 0.3576 + b * 0.1805
        y = r * 0.2126 + g * 0.7152 + b * 0.0722
        z = r * 0.0193 + g * 0.1192 + b * 0.9505
        return cls(x * 100, y * 100, z * 100)
    
    def with_x(self, val) -> RGB:
        return self._with_a(val)
    
    def with_y(self, val) -> RGB:
        return self._with_b(val)
    
    def with_z(self, val) -> RGB:
        return self._with_c(val)

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

        y = (self.l + 16) / 116
        x = self.a / 500 + y
        z = y - self.b / 200
        return XYZ(95.047 * f(x), 100 * f(y), 108.883 * f(z), clamp = True)

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
    def from_full_rgb(cls, *rgb: tuple[float, float, float]):
        # rgb to lab, using xyz as an intermediate step
        rgb = cls._check_rgb_args(rgb)
        return cls._from_xyz(XYZ.from_full_rgb(rgb))

    def with_l(self, val) -> RGB:
        return self._with_a(val)
    
    def with_a(self, val) -> RGB:
        return self._with_b(val)
    
    def with_b(self, val) -> RGB:
        return self._with_c(val)

    
@dataclass(frozen = True, slots = True)
class OKLAB(ColorModel):
    l: float
    a: float
    b: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, None), (None, None), (None, None))

    def _to_xyz(self) -> XYZ:
        # https://en.wikipedia.org/wiki/Oklab_color_space
        M_1_inv = [
            [ 1.22701385, -0.55779996,  0.28125615],
            [-0.04058018,  1.11225687, -0.07167668],
            [-0.07638128, -0.42148198,  1.58616322]
        ]
        M_2_inv = [
            [ 1.        ,  0.39633779,  0.21580376],
            [ 1.00000001, -0.10556134, -0.06385417],
            [ 1.00000005, -0.08948418, -1.29148554]
        ]

        l = M_2_inv[0][0] * self.l + M_2_inv[0][1] * self.a + M_2_inv[0][2] * self.b
        m = M_2_inv[1][0] * self.l + M_2_inv[1][1] * self.a + M_2_inv[1][2] * self.b
        s = M_2_inv[2][0] * self.l + M_2_inv[2][1] * self.a + M_2_inv[2][2] * self.b

        l = l ** 3
        m = m ** 3
        s = s ** 3

        x = M_1_inv[0][0] * l + M_1_inv[0][1] * m + M_1_inv[0][2] * s
        y = M_1_inv[1][0] * l + M_1_inv[1][1] * m + M_1_inv[1][2] * s
        z = M_1_inv[2][0] * l + M_1_inv[2][1] * m + M_1_inv[2][2] * s

        return XYZ(x * 100, y * 100, z * 100, clamp = True)

    @classmethod
    def _from_xyz(cls, xyz: XYZ):
        # https://en.wikipedia.org/wiki/Oklab_color_space
        
        M_1 = [
            [ 0.8189330101,  0.3618667242, -0.1288597137],
            [ 0.0329845436,  0.9293118715,  0.0361456387],
            [ 0.0482003018,  0.2643662691,  0.6338517070]
        ]
        M_2 = [
            [ 0.2104542553,  0.7936177850, -0.0040720468],
            [ 1.9779984951, -2.4285922020,  0.4505937099],
            [ 0.0259040371,  0.7827717662, -0.8086757660]
        ]

        X, Y, Z = xyz
        X /= 100
        Y /= 100
        Z /= 100

        l = M_1[0][0] * X + M_1[0][1] * Y + M_1[0][2] * Z
        m = M_1[1][0] * X + M_1[1][1] * Y + M_1[1][2] * Z
        s = M_1[2][0] * X + M_1[2][1] * Y + M_1[2][2] * Z

        l = l ** (1/3)
        m = m ** (1/3)
        s = s ** (1/3)

        
        L = M_2[0][0] * l + M_2[0][1] * m + M_2[0][2] * s
        a = M_2[1][0] * l + M_2[1][1] * m + M_2[1][2] * s
        b = M_2[2][0] * l + M_2[2][1] * m + M_2[2][2] * s

        return cls(L, a, b)

    
    def to_full_rgb(self) -> tuple[float, float, float]:
        # lab to rgb, using xyz as an intermediate step
        return self._to_xyz().to_full_rgb()

    @classmethod
    def from_full_rgb(cls, *rgb: tuple[float, float, float]):
        # rgb to lab, using xyz as an intermediate step
        rgb = cls._check_rgb_args(rgb)
        return cls._from_xyz(XYZ.from_full_rgb(rgb))

    def with_l(self, val) -> RGB:
        return self._with_a(val)
    
    def with_a(self, val) -> RGB:
        return self._with_b(val)
    
    def with_b(self, val) -> RGB:
        return self._with_c(val)


@dataclass(frozen = True, slots = True)
class OKLCH(ColorModel):
    l: float
    c: float
    h: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, None), (None, None), (None, None))

    def _normalize(self):
        object.__setattr__(self, "h", float(self.h % 360))

    @classmethod
    def _from_oklab(cls, oklab: OKLAB) -> OKLCH:
        L = oklab.l
        C = (oklab.a ** 2 + oklab.b ** 2) ** (1/2)
        h = math.degrees(math.atan2(oklab.b, oklab.a))
        return cls(L, C, h)

    def _to_oklab(self) -> OKLAB:
        L = self.l
        a = self.c * math.cos(math.radians(self.h))
        b = self.c * math.sin(math.radians(self.h))
        return OKLAB(L, a, b)

    
    def to_full_rgb(self) -> tuple[float, float, float]:
        # lab to rgb, using xyz as an intermediate step
        return self._to_oklab().to_full_rgb()

    @classmethod
    def from_full_rgb(cls, *rgb: tuple[float, float, float]):
        # rgb to lab, using oklab as an intermediate step
        rgb = cls._check_rgb_args(rgb)
        return cls._from_oklab(OKLAB.from_full_rgb(rgb))

    def with_l(self, val) -> RGB:
        return self._with_a(val)
    
    def with_c(self, val) -> RGB:
        return self._with_b(val)
    
    def with_h(self, val) -> RGB:
        return self._with_c(val)
    