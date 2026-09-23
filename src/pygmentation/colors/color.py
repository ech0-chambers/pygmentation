from .models import ColorModel, RGB, HSL, HSV, XYZ, LAB, OKLAB, OKLCH
from functools import cached_property
import math

class Color:
    def __init__(self, color: str | ColorModel):
        if isinstance(color, str):
            color = RGB.from_hex(color)

        self._full_rgb = color.to_full_rgb()

    @cached_property
    def hex(self) -> str:
        return self.rgb.to_hex()

    @cached_property
    def rgb(self) -> RGB:
        return RGB.from_full_rgb(*self._full_rgb)

    @cached_property
    def hsl(self) -> HSL:
        return HSL.from_full_rgb(*self._full_rgb)

    @cached_property
    def hsv(self) -> HSV:
        return HSV.from_full_rgb(*self._full_rgb)

    @cached_property
    def xyz(self) -> XYZ:
        return XYZ.from_full_rgb(*self._full_rgb)

    @cached_property
    def lab(self) -> LAB:
        return LAB.from_full_rgb(*self._full_rgb)

    @cached_property
    def oklab(self) -> OKLAB:
        return OKLAB.from_full_rgb(*self._full_rgb)
    
    @cached_property
    def oklch(self) -> OKLAB:
        return OKLCH.from_full_rgb(*self._full_rgb)

    @property
    def r(self) -> int:
        return self.rgb.r
    @property
    def g(self) -> int:
        return self.rgb.g
    @property
    def b(self) -> int:
        return self.rgb.b
    @property
    def h(self) -> int:
        return self.hsl.h
    @property
    def s(self) -> int:
        return self.hsl.s
    @property
    def l(self) -> int:
        return self.hsl.l


    def with_r(self, r: float) -> Color:
        return Color(self.rgb.with_r(r))

    def with_g(self, g: float) -> Color:
        return Color(self.rgb.with_g(g))

    def with_b(self, b: float) -> Color:
        return Color(self.rgb.with_b(b))

    def with_h(self, h: float) -> Color:
        return Color(self.hsl.with_h(h))

    def with_s(self, s: float) -> Color:
        return Color(self.hsl.with_s(s))

    def with_l(self, l: float) -> Color:
        return Color(self.hsl.with_l(l))

    def lighten(self, amount: float, target_lightness: float = 1) -> Color:
        if amount > 1:
            amount /= 100

        new_l = self.oklab.l + (target_lightness - self.oklab.l) * amount
        return Color(self.oklab.with_l(new_l))
    
    def darken(self, amount: float, target_lightness: float = 0) -> Color:
            if amount > 1:
                amount /= 100
    
            new_l = self.oklab.l - (self.oklab.l - target_lightness) * amount
            return Color(self.oklab.with_l(new_l))

    tint = lighten
    shade = darken

    def hue_diff(self, other: Color) -> float:
        return (other.h - self.h + 180) % 360 - 180

    def hue_diff_oklch(self, other: Color) -> float:
        return (other.oklch.h - self.oklch.h + 180) % 360 - 180

    def lerp(self, other: Color, amount: float) -> Color:
        if amount > 1:
            amount /= 100
        new_l = self.oklab.l + (other.oklab.l - self.oklab.l) * amount
        new_a = self.oklab.a + (other.oklab.a - self.oklab.a) * amount
        new_b = self.oklab.b + (other.oklab.b - self.oklab.b) * amount
        return Color(OKLAB(new_l, new_a, new_b))
        
    def distance_to(self, other):
        # Returns a measure of similarity between self and other, based on https://github.com/hamada147/IsThisColourSimilar
        lab1 = self.lab
        lab2 = other.lab

        l1, a1, b1 = lab1.as_tuple()
        l2, a2, b2 = lab2.as_tuple()

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

        h1p = math.degrees(math.atan2(b1, a1p))
        if h1p < 0:
            h1p += 360

        h2p = math.degrees(math.atan2(b2, a2p))
        if h2p < 0:
            h2p += 360

        if abs(h1p - h2p) > 180:
            avgHp = (h1p + h2p + 360) / 2
        else:
            avgHp = (h1p + h2p) / 2

        t = (
            1
            - 0.17 * math.cos(math.radians(avgHp - 30))
            + 0.24 * math.cos(math.radians(2 * avgHp))
            + 0.32 * math.cos(math.radians(3 * avgHp + 6))
            - 0.2 * math.cos(math.radians(4 * avgHp - 63))
        )

        deltaHp = h2p - h1p
        if abs(deltaHp) > 180:
            if h2p <= h1p:
                deltaHp += 360
            else:
                deltaHp -= 360

        deltaLp = l2 - l1
        deltaCp = c2p - c1p
        deltaHp = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(deltaHp) / 2)

        sL = 1 + ((0.015 * (avgL - 50) ** 2) / math.sqrt(20 + (avgL - 50) ** 2))
        sC = 1 + 0.045 * avgCp
        sH = 1 + 0.015 * avgCp * t

        deltaRho = 30 * math.exp(-(((avgHp - 275) / 25) ** 2))
        rc = 2 * math.sqrt((avgCp**7) / (avgCp**7 + 25**7))
        rt = -rc * math.sin(2 * math.radians(deltaRho))

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

    def __eq__(self, other) -> bool:
        return self.hex == other.hex

    def __hash__(self):
        return hash(self.hex)