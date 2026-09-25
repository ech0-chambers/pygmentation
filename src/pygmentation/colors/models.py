from abc import ABC, abstractmethod
from enum import IntEnum
from typing import ClassVar, Final
import math
from dataclasses import dataclass, InitVar, fields


class ColorModel(ABC):
    BOUNDS: tuple[tuple[float | None, float | None], ...] = ()
    _registry: ClassVar[dict[str, type["ColorModel"]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Automatically registers "rgb", "hsl", "hsv", "xyz", "lab", "oklab", "oklch"
        cls._registry[cls.__name__.lower()] = cls


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
                    if math.isclose(val, low, abs_tol=1e-5, rel_tol=1e-5):
                        object.__setattr__(self, field.name, low)
                    else:
                        raise ValueError(f"Value {val} is below minimum {low}")
                if high is not None and val > high:
                    if math.isclose(val, high, abs_tol=1e-5, rel_tol=1e-5):
                        object.__setattr__(self, field.name, high)
                    else:
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
    def to_xyz(self) -> tuple[float]:
        pass

    @classmethod
    @abstractmethod
    def from_xyz(*xyz: tuple[float]) -> ColorModel:
        pass

    @staticmethod
    def _check_xyz_args(xyz: tuple[float] | tuple[tuple[float]]) -> tuple[float]:
        if len(xyz) == 1 and isinstance(xyz[0], (tuple, list)):
            xyz = xyz[0]
        if not len(xyz) == 3:
            raise ValueError(f"Expected 3 xyz values, but received {len(xyz)}")
        return xyz

    def convert_to(self, new_model: str | type[ColorModel]):
        if isinstance(new_model, str):
            name = new_model.lower()
            if name == "hex":
                if isinstance(self, RGB):
                    return self.to_hex()
                return RGB.from_xyz(self.to_xyz()).to_hex()
            if name == "css":
                if isinstance(self, RGB):
                    return f"#{self.to_hex()}"
                return f"#{RGB.from_xyz(self.to_xyz()).to_hex()}"

            if name not in self._registry:
                raise ValueError(f"Unknown color model: {new_model}. Available models: {list(self._registry.keys())}")

            target_cls = self._registry[name]
        elif isinstance(new_model, type) and issubclass(new_model, ColorModel):
            target_cls = new_model
        else:
            raise TypeError(f"Expected model name (str) or ColorModel subclass, got {new_model!r}")
        
        if isinstance(self, target_cls):
            return self

        # Direct conversions
        if isinstance(self, OKLAB) and target_cls is OKLCH:
            return OKLCH._from_oklab(self)
        if isinstance(self, OKLCH) and target_cls is OKLAB:
            return self._to_oklab()

        
        return target_cls.from_xyz(self.to_xyz())

    def as_tuple(self):
        return tuple(self)

    def _with_a(self, val: float) -> ColorModel:
        return self.__class__(val, self._b, self._c)

    def _with_b(self, val: float) -> ColorModel:
        return self.__class__(self._a, val, self._c)
    
    def _with_c(self, val: float) -> ColorModel:
        return self.__class__(self._a, self._b, val)


def _rgb_float_to_xyz(rgb: tuple[float]) -> tuple[float]:
    # Convert rgb float [0,1] to xyz float [0,inf]
    r, g, b = (
        x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb
    )
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    return x * 100, y * 100, z * 100

def _xyz_to_rgb_float(xyz: tuple[float]) -> tuple[float]:
    x, y, z = (x / 100 for x in xyz)
    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570
    r = 12.92 * r if r <= 0.0031308 else (1.055 * r ** (1 / 2.4)) - 0.055
    g = 12.92 * g if g <= 0.0031308 else (1.055 * g ** (1 / 2.4)) - 0.055
    b = 12.92 * b if b <= 0.0031308 else (1.055 * b ** (1 / 2.4)) - 0.055
    return r,g,b


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

    def to_xyz(self) -> tuple[float, float, float]:
        rgb = (v / 255 for v in self)
        return _rgb_float_to_xyz(rgb)

    @classmethod
    def from_xyz(cls, *xyz: tuple[float, float, float]) -> RGB:
        xyz = cls._check_xyz_args(xyz)
        rgb = _xyz_to_rgb_float(xyz)
        r,g,b = (int(round(v * 255)) for v in rgb)
        return cls(r, g, b, clamp = True)

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

    def _to_full_rgb(self) -> tuple[float, float, float]:
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
    def _from_full_rgb(cls, *rgb: tuple[float]) -> HSL:
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        rgb = cls._check_xyz_args(rgb)
        r, g, b = (min(1.0, max(0.0, float(x))) for x in rgb)
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
        return cls(h, s, l, clamp = True)

    def to_xyz(self) -> tuple[float]:
        rgb = self._to_full_rgb()
        return _rgb_float_to_xyz(rgb)

    @classmethod
    def from_xyz(cls, *xyz: tuple[float, float, float]) -> HSL:
        xyz = cls._check_xyz_args(xyz)
        rgb = _xyz_to_rgb_float(xyz)
        return cls._from_full_rgb(rgb)

    def with_h(self, val) -> HSL:
        return self._with_a(val)
    
    def with_s(self, val) -> HSL:
        return self._with_b(val)
    
    def with_l(self, val) -> HSL:
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

    def _to_full_rgb(self) -> tuple[float, float, float]:
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
    def _from_full_rgb(cls, *rgb: tuple[float]):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        rgb = cls._check_xyz_args(rgb)
        r, g, b = (min(1.0, max(0.0, float(x))) for x in rgb)
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
        return cls(h, s, v, clamp = True)

    def to_xyz(self) -> tuple[float]:
        rgb = self._to_full_rgb()
        return _rgb_float_to_xyz(rgb)

    @classmethod
    def from_xyz(cls, *xyz: tuple[float, float, float]) -> HSV:
        xyz = cls._check_xyz_args(xyz)
        rgb = _xyz_to_rgb_float(xyz)
        return cls._from_full_rgb(rgb)

    def with_h(self, val) -> HSV:
        return self._with_a(val)
    
    def with_s(self, val) -> HSV:
        return self._with_b(val)
    
    def with_v(self, val) -> HSV:
        return self._with_c(val)

@dataclass(frozen = True, slots = True)
class XYZ(ColorModel):
    x: float
    y: float
    z: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, None), (0, None), (0, None))
    

    def to_xyz(self) -> tuple[float]:
        return tuple(self)

    @classmethod
    def from_xyz(cls, *xyz: tuple[float, float, float]) -> XYZ:
        xyz = cls._check_xyz_args(xyz)
        return XYZ(*xyz, clamp = True)
    
    def with_x(self, val) -> XYZ:
        return self._with_a(val)
    
    def with_y(self, val) -> XYZ:
        return self._with_b(val)
    
    def with_z(self, val) -> XYZ:
        return self._with_c(val)

@dataclass(frozen = True, slots = True)
class LAB(ColorModel):
    l: float
    a: float
    b: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, None), (None, None), (None, None))

    def to_xyz(self) -> tuple[float]:
        # https://en.wikipedia.org/wiki/CIELAB_color_space
        def f(t):
            if t > 6 / 29:
                return t**3
            return (t - 4 / 29) / 7.787

        y = (self.l + 16) / 116
        x = self.a / 500 + y
        z = y - self.b / 200
        return 95.047 * f(x), 100 * f(y), 108.883 * f(z)

    @classmethod
    def from_xyz(cls, *xyz: tuple[float]) -> LAB:
        # https://en.wikipedia.org/wiki/CIELAB_color_space
        xyz = cls._check_xyz_args(xyz)

        def f(t):
            delta = 6 / 29
            if t > delta**3:
                return t ** (1 / 3)
            return t / (3 * delta**2) + 4 / 29

        x,y,z = xyz

        Xn = 95.0489
        Yn = 100
        Zn = 108.8840
        x = f(x / Xn)
        y = f(y / Yn)
        z = f(z / Zn)
        return cls(116 * y - 16, 500 * (x - y), 200 * (y - z), clamp = True)

    def with_l(self, val) -> LAB:
        return self._with_a(val)
    
    def with_a(self, val) -> LAB:
        return self._with_b(val)
    
    def with_b(self, val) -> LAB:
        return self._with_c(val)

    
@dataclass(frozen = True, slots = True)
class OKLAB(ColorModel):
    l: float
    a: float
    b: float
    clamp: InitVar[bool] = False
    BOUNDS = ((0, None), (None, None), (None, None))

    def to_xyz(self) -> XYZ:
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

        return x * 100, y * 100, z * 100

    @classmethod
    def from_xyz(cls, *xyz: XYZ) -> OKLAB:
        # https://en.wikipedia.org/wiki/Oklab_color_space
        xyz = cls._check_xyz_args(xyz)
        
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

        return cls(L, a, b, clamp = True)

    def with_l(self, val) -> OKLAB:
        return self._with_a(val)
    
    def with_a(self, val) -> OKLAB:
        return self._with_b(val)
    
    def with_b(self, val) -> OKLAB:
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
        return cls(L, C, h, clamp = True)

    def _to_oklab(self) -> OKLAB:
        L = self.l
        a = self.c * math.cos(math.radians(self.h))
        b = self.c * math.sin(math.radians(self.h))
        return OKLAB(L, a, b)

    
    def to_xyz(self) -> tuple[float]:
        return self._to_oklab().to_xyz()

    @classmethod
    def from_xyz(cls, *xyz: XYZ) -> OKLCH:
        xyz = cls._check_xyz_args(xyz)
        return cls._from_oklab(OKLAB.from_xyz(xyz))


    def with_l(self, val) -> OKLCH:
        return self._with_a(val)
    
    def with_c(self, val) -> OKLCH:
        return self._with_b(val)
    
    def with_h(self, val) -> OKLCH:
        return self._with_c(val)
    