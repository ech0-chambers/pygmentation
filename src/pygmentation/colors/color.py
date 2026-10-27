from __future__ import annotations

import math
from functools import cached_property

from .models import _RGB_255, HSL, HSV, LAB, OKLAB, OKLCH, RGB, XYZ, ColorModel


class Color:
    """
    Store and handle a colour, allowing conversions between colour models and
    colour manipulations.

    Parameters
    ----------
    color : str | ColorModel | Color
        The colour to store. If a `str`, it should be a 6-character hex string
        with or without a leading `#`. Any further characters (such as an alpha
        channel) will be ignored. Regardless of argument type, it will be stored
        in the Oklab colour model.

    Attributes
    ----------
    hex : str
        The colour as an (uppercase) 6-character hex string, without a leading
        `#`.
    css : str
        The colour as an (uppercase) 6-character hex string, with a leading `#`.
    rgb : RGB
        The colour in the sRGB colour model as floats between 0.0 and 1.0.
    as_255 : _RGB_255
        The colour in the sRGB colour model as integers between 0 and 255, as a
        named tuple with properties `r`, `g`, and `b`.
    hsl : HSL
        The colour in the HSL colour model, with hue in degrees (0 to 360) and
        saturation and lightness as floats between 0.0 and 1.0.
    hsv : HSV
        The colour in the HSV colour model, with hue in degrees (0 to 360) and
        saturation and value as floats between 0.0 and 1.0.
    xyz : XYZ
        The colour in the CIE XYZ colour model.
    lab : LAB
        The colour in the CIELAB (CIE L*a*b*) colour model.
    oklab : OKLAB
        The colour in the Oklab colour model (the internal storage
        representation).
    oklch : OKLCH
        The colour in the Oklch (cylindrical Oklab) colour model.
    r : float
        Red channel value in sRGB as a float between 0.0 and 1.0 (convenience
        property for `rgb.r`).
    g : float
        Green channel value in sRGB as a float between 0.0 and 1.0 (convenience
        property for `rgb.g`).
    b : float
        Blue channel value in sRGB as a float between 0.0 and 1.0 (convenience
        property for `rgb.b`).
    h : float
        Hue value in HSL in degrees between 0.0 and 360.0 (convenience property
        for `hsl.h`).
    s : float
        Saturation value in HSL as a float between 0.0 and 1.0 (convenience
        property for `hsl.s`).
    l : float
        Lightness value in HSL as a float between 0.0 and 1.0 (convenience
        property for `hsl.l`).
    """
    def __init__(self, color: str | ColorModel | Color):
        if isinstance(color, str):
            self._oklab: OKLAB = RGB.from_hex(color).convert_to(OKLAB)
        elif isinstance(color, OKLAB):
            self._oklab = color
        elif isinstance(color, Color):
            self._oklab = color.oklab
        else:
            self._oklab = color.convert_to(OKLAB)

    def copy(self) -> Color:
        """
        Returns a new `Color` instance with the same value.

        Returns
        -------
        Color
            The new `Color` instance.
        """
        return Color(self.oklab)

    @cached_property
    def hex(self) -> str:
        return self.rgb.to_hex()

    @cached_property
    def css(self) -> str:
        return "#" + self.hex

    @cached_property
    def rgb(self) -> RGB:
        return self._oklab.convert_to(RGB)

    @property
    def as_255(self) -> _RGB_255:
        return self.rgb.as_255

    @cached_property
    def hsl(self) -> HSL:
        return self._oklab.convert_to(HSL)

    @cached_property
    def hsv(self) -> HSV:
        return self._oklab.convert_to(HSV)

    @cached_property
    def xyz(self) -> XYZ:
        return self._oklab.convert_to(XYZ)

    @cached_property
    def lab(self) -> LAB:
        return self._oklab.convert_to(LAB)

    @cached_property
    def oklab(self) -> OKLAB:
        return self._oklab

    @cached_property
    def oklch(self) -> OKLCH:
        return self._oklab.convert_to(OKLCH)

    @property
    def r(self) -> float:
        return self.rgb.r

    @property
    def g(self) -> float:
        return self.rgb.g

    @property
    def b(self) -> float:
        return self.rgb.b

    @property
    def h(self) -> float:
        return self.hsl.h

    @property
    def s(self) -> float:
        return self.hsl.s

    @property
    def l(self) -> float:
        return self.hsl.l

    def with_r(self, r: float) -> Color:
        """
        Create a new `Color` instance whose sRGB representation has the same
        green and blue channel values, but the specified red channel value.

        Parameters
        ----------
        r : float
            New value for the red channel.

        Returns
        -------
        Color
            A new `Color` instance whose sRGB representation has the same green
            and blue channel values, but the specified red channel value.
        """
        return Color(self.rgb.with_r(r))

    def with_g(self, g: float) -> Color:
        """
        Create a new `Color` instance whose sRGB representation has the same red
        and blue channel values, but the specified green channel value.

        Parameters
        ----------
        g : float
            New value for the green channel.

        Returns
        -------
        Color
            A new `Color` instance whose sRGB representation has the same red
            and blue channel values, but the specified green channel value.
        """
        return Color(self.rgb.with_g(g))

    def with_b(self, b: float) -> Color:
        """
        Create a new `Color` instance whose sRGB representation has the same red
        and green channel values, but the specified blue channel value.

        Parameters
        ----------
        b : float
            New value for the blue channel.

        Returns
        -------
        Color
            A new `Color` instance whose sRGB representation has the same red
            and green channel values, but the specified blue channel value.
        """
        return Color(self.rgb.with_b(b))

    def with_h(self, h: float) -> Color:
        """
        Create a new `Color` instance whose HSL representation has the same
        saturation and lightness channel values, but the specified hue value.

        Parameters
        ----------
        h : float
            New value for the hue channel (in degrees).

        Returns
        -------
        Color
            A new `Color` instance whose HSL representation has the same
            saturation and lightness channel values, but the specified hue
            value.
        """
        return Color(self.hsl.with_h(h))

    def with_s(self, s: float) -> Color:
        """
        Create a new `Color` instance whose HSL representation has the same hue
        and lightness channel values, but the specified saturation value.

        Parameters
        ----------
        s : float
            New value for the saturation channel.

        Returns
        -------
        Color
            A new `Color` instance whose HSL representation has the same hue and
            lightness channel values, but the specified saturation value.
        """
        return Color(self.hsl.with_s(s))

    def with_l(self, l: float) -> Color:
        """
        Create a new `Color` instance whose HSL representation has the same hue
        and saturation channel values, but the specified lightness value.

        Parameters
        ----------
        l : float
            New value for the lightness channel.

        Returns
        -------
        Color
            A new `Color` instance whose HSL representation has the same hue and
            saturation channel values, but the specified lightness value.
        """
        return Color(self.hsl.with_l(l))

    def lighten(
        self, amount: float, target_lightness: float = 1, percentage: bool = False
    ) -> Color:
        r"""
        Lightens the colour by the specified amount in the Oklab colour space.
        The new lightness is $\text{amount} \times 100\%$ closer to the target
        lightness than the original. In other words, for an original lightness
        $l$, a target lightness $l_T$, and an amount $a$, the new lightness
        $l^\prime = l + (l_T - l) * a$.

        Parameters
        ----------
        amount : float
            The amount by which to lighten the colour. This should be between 0
            and 1, unless `percentage = True`, in which case it should be
            between 0 and 100.
        target_lightness : float, optional
            The target lightness towards which the colour is moved.
        percentage : bool, optional
            If `True`, the `amount` is treated as a percentage rather than a
            factor.

        Returns
        -------
        Color
            A new `Color` instance, with the altered Oklab lightness, but
            unchanged $a$ and $b$ channels in Oklab colour space.
        """
        if percentage:
            amount /= 100

        new_l = self.oklab.l + (target_lightness - self.oklab.l) * amount
        return Color(self.oklab.with_l(new_l))

    def darken(
        self, amount: float, target_lightness: float = 0, percentage: bool = False
    ) -> Color:
        r"""
        Darkens the colour by the specified amount in the Oklab colour space.
        The new lightness is $\text{amount} \times 100\%$ closer to the target
        lightness than the original. In other words, for an original lightness
        $l$, a target lightness $l_T$, and an amount $a$, the new lightness
        $l^\prime = l - (l - l_T) * a$.

        Parameters
        ----------
        amount : float
            The amount by which to darken the colour. This should be between 0
            and 1, unless `percentage = True`, in which case it should be
            between 0 and 100.
        target_lightness : float, optional
            The target lightness towards which the colour is moved.
        percentage : bool, optional
            If `True`, the `amount` is treated as a percentage rather than a
            factor.

        Returns
        -------
        Color
            A new `Color` instance, with the altered Oklab lightness, but
            unchanged $a$ and $b$ channels in Oklab colour space.
        """
        if percentage:
            amount /= 100

        new_l = self.oklab.l - (self.oklab.l - target_lightness) * amount
        return Color(self.oklab.with_l(new_l))

    tint = lighten
    shade = darken

    def hue_diff(self, other: Color) -> float:
        """
        Calculate the shortest signed difference in hue between this colour and
        another colour in the HSL colour space.

        Parameters
        ----------
        other : Color
            The other colour to compare against.

        Returns
        -------
        float
            The signed hue difference in degrees in the range $[-180, 180)$. A
            positive value indicates that `other` has a larger hue angle than
            `self`.
        """
        return (other.h - self.h + 180) % 360 - 180

    def hue_diff_oklch(self, other: Color) -> float:
        """
        Calculate the shortest signed difference in hue between this colour and
        another colour in the Oklch colour space.

        Parameters
        ----------
        other : Color
            The other colour to compare against.

        Returns
        -------
        float
            The signed hue difference in degrees in the range $[-180, 180)$ in
            Oklch colour space. A positive value indicates that `other` has a
            larger hue angle than `self`.
        """
        return (other.oklch.h - self.oklch.h + 180) % 360 - 180

    def lerp(self, other: Color, amount: float, percentage: bool = False) -> Color:
        """
        Linearly interpolate between this colour and another colour in the Oklab
        colour space.

        Parameters
        ----------
        other : Color
            The target colour to interpolate towards.
        amount : float
            The interpolation factor between this colour and `other`. This
            should be between 0 and 1, unless `percentage = True`, in which case
            it should be between 0 and 100.
        percentage : bool, optional
            If `True`, the `amount` is treated as a percentage rather than a
            factor.

        Returns
        -------
        Color
            A new `Color` instance representing the interpolated colour in Oklab
            colour space.
        """
        if percentage:
            amount /= 100
        new_l = self.oklab.l + (other.oklab.l - self.oklab.l) * amount
        new_a = self.oklab.a + (other.oklab.a - self.oklab.a) * amount
        new_b = self.oklab.b + (other.oklab.b - self.oklab.b) * amount
        return Color(OKLAB(new_l, new_a, new_b))

    def distance_to_CIEDE2000(self, other: Color | ColorModel | str) -> float:
        r"""
        Calculate the full colour distance $\Delta E_{00}$ according to the CIE
        DE2000 algorithm. Note that this is only valid for similar colours with
        $\Delta E_{00} \leq 5$. For larger distances, use the
        `Color.distance_to(other)` method.

        Parameters
        ----------
        other : Color | ColorModel | str
            The other colour to compare. This can be a `Color` instance, an
            instance of any `ColorModel`, or a 6-character hex string, with or
            without a leading `#`. The latter two will be converted to the
            necessary colour space prior to comparison.

        Returns
        -------
        float
            The $\Delta E_{00}$ colour distance between the two colours.
        """
        # Returns a measure of similarity between self and other, based on https://github.com/hamada147/IsThisColourSimilar

        if not isinstance(other, Color):
            other = Color(other)

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

    def distance_to(self, other: Color | ColorModel | str) -> float:
        """
        Calculate the Euclidean distance to the `other` colour in Oklab space.
        This is reliable over any distance, but for very similar colours
        consider whether `Color.distance_to_CIEDE2000(other)` is more
        appropriate.

        Parameters
        ----------
        other : Color | ColorModel | str
            The other colour to compare. This can be a `Color` instance, an
            instance of any `ColorModel`, or a 6-character hex string, with or
            without a leading `#`. The latter two will be converted to the Oklab
            colour space prior to comparison.

        Returns
        -------
        float
            DescriptionThe Euclidean distance from `self` to `other` in the
            Oklab colour space.
        """

        # Euclidean distance in OKLAB space

        if not isinstance(other, Color):
            other = Color(other)

        dl = self._oklab.l - other._oklab.l
        da = self._oklab.a - other._oklab.a
        db = self._oklab.b - other._oklab.b

        return 100 * math.sqrt(dl**2 + da**2 + db**2)

    def is_darker_than(self, other: Color | ColorModel | str) -> bool:
        """
        Tests if this colour has a lower lightness than `other` in the Oklab
        colour space.

        Parameters
        ----------
        other : Color
            The other colour to compare. This can be a `Color` instance, an
            instance of any `ColorModel`, or a 6-character hex string, with or
            without a leading `#`. The latter two will be converted to the Oklab
            colour space prior to comparison.

        Returns
        -------
        bool
            `True` if `self` is darker than `other`, otherwise `False`. Note
            this is also `False` if the lightness is identical.
        """

        if not isinstance(other, Color):
            other = Color(other)
        return self.oklab.l < other.oklab.l

    def is_lighter_than(self, other: Color | ColorModel | str) -> bool:
        """
        Tests if this colour has a higher lightness than `other` in the Oklab
        colour space.

        Parameters
        ----------
        other : Color
            The other colour to compare. This can be a `Color` instance, an
            instance of any `ColorModel`, or a 6-character hex string, with or
            without a leading `#`. The latter two will be converted to the Oklab
            colour space prior to comparison.

        Returns
        -------
        bool
            `True` if `self` is lighter than `other`, otherwise `False`. Note
            this is also `False` if the lightness is identical.
        """

        if not isinstance(other, Color):
            other = Color(other)
        return self.oklab.l > other.oklab.l

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return False
        return self.hex == other.hex

    def __hash__(self) -> int:
        return hash(self.hex)

    def __str__(self) -> str:
        return self.css

    def __repr__(self) -> str:
        return f"Color('{self.css}')"
