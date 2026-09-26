from enum import StrEnum
from itertools import combinations
from .color import Color
from .models import ColorModel, OKLCH, OKLAB
from collections import Counter


class SchemeType(StrEnum):
    EMPTY = "empty"
    LIGHT = "light"
    DARK = "dark"


class ColorFamily:

    __HUE_DIFF_THRESHOLD = 30
    __MIN_TARGET_LIGHTNESS = 0.2
    __MAX_TARGET_LIGHTNESS = 0.8

    def __init__(
        self,
        base: Color | str | ColorModel,
        scheme_type: SchemeType | str,
        light: Color | str | ColorModel | None = None,
        dark: Color | str | ColorModel | None = None,
        is_main: bool = False,
        variants: list[Color | ColorModel | str] | None = None,
    ):
        if not isinstance(base, Color):
            base = Color(base)

        if light is None:
            light = Color("#FFFFFF")
        else:
            if not isinstance(light, Color):
                light = Color(light)

        if dark is None:
            dark = Color("#000000")
        else:
            if not isinstance(dark, Color):
                dark = Color(dark)

        if light.is_darker_than(dark):
            light, dark = dark, light

        if not isinstance(scheme_type, SchemeType):
            try:
                scheme_type = SchemeType[scheme_type.upper()]
            except KeyError as e:
                print(f"Scheme type `{scheme_type}` is not recognised.")
                raise e

        self._base = base
        self._light = light
        self._dark = dark
        self._scheme_type = scheme_type

        if variants is not None:
            if len(variants) != 5:
                raise ValueError(
                    f"ColorFamily requires exactly 5 variants, got {len(variants)}"
                )
            self.variants = [v if isinstance(v, Color) else Color(v) for v in variants]
            return

        # We check if the base colour is too dark to have darker variants, or too light to have lighter variants
        too_light = self._base.oklab.l / self._light.oklab.l > 0.9
        too_dark = self._base.oklab.l - self._dark.oklab.l < 0.2

        amounts = [0] * 5

        # If it's a foreground/background colour (is_main), the variants are from 5% to 50% lighter/darker
        # In most cases, we generate two darker variants (50%, 25%) and three lighter variants (40%, 60%, 80%) (or vice versa for dark schemes)
        # If the colour is too light/dark to generate even lighter/darker variants, we instead generate 5 darker/lighter variants from 90% to 10%

        if self._scheme_type == SchemeType.LIGHT:
            if too_light:
                if is_main:
                    amounts = [-0.5, -0.25, -0.15, -0.1, -0.05]
                else:
                    amounts = [-0.9, -0.75, -0.5, -0.25, -0.1]
            elif too_dark:
                if is_main:
                    amounts = [0.05, 0.1, 0.15, 0.25, 0.5]
                else:
                    amounts = [0.1, 0.25, 0.5, 0.75, 0.9]
            else:
                amounts = [-0.5, -0.25, 0.4, 0.6, 0.8]
        elif self._scheme_type == SchemeType.DARK:
            if too_light:
                if is_main:
                    amounts = [-0.05, -0.1, -0.15, -0.25, -0.5]
                else:
                    amounts = [-0.1, -0.25, -0.5, -0.75, -0.9]
            elif too_dark:
                if is_main:
                    amounts = [0.5, 0.25, 0.15, 0.1, 0.05]
                else:
                    amounts = [0.9, 0.75, 0.5, 0.25, 0.1]
            else:
                amounts = [0.5, 0.25, -0.4, -0.6, -0.8]
        else:
            raise ValueError(f"Invalid scheme type '{self._scheme_type}'")

        self.variants = []

        for amount in amounts:
            if amount < 0:
                self.variants.append(self.darker(amount))
            else:
                self.variants.append(self.lighter(amount))

    def darker(self, amount: float) -> Color:
        # If the "dark" colour provided has a similar hue to the base colour, we'll also subtly shift towards that hue rather than just changing the lightness
        use_dark = (
            abs(self._base.hue_diff_oklch(self._dark)) < self.__HUE_DIFF_THRESHOLD
        )

        if use_dark:
            return self._base.lerp(self._dark, abs(amount))
        return self._base.darken(
            abs(amount), max(self.__MIN_TARGET_LIGHTNESS, self._dark.oklab.l)
        )

    def lighter(self, amount: float) -> Color:
        # If the "light" colour provided has a similar hue to the base colour, we'll also subtly shift towards that hue rather than just changing the lightness
        use_light = (
            abs(self._base.hue_diff_oklch(self._light)) < self.__HUE_DIFF_THRESHOLD
        )

        if use_light:
            return self._base.lerp(self._light, abs(amount))
        return self._base.lighten(
            abs(amount), min(self.__MAX_TARGET_LIGHTNESS, self._light.oklab.l)
        )

    def __getitem__(self, index: int) -> Color:
        if isinstance(index, slice):
            return [self[i] for i in range(len(self.variants) + 1)[index]]

        if index == 0:
            return self._base
        return self.variants[index - 1]

    @property
    def base(self) -> Color:
        return self._base

    @property
    def lightest(self) -> Color:
        if self._scheme_type == SchemeType.LIGHT:
            return self.variants[4]
        return self.variants[0]

    @property
    def darkest(self) -> Color:
        if self._scheme_type == SchemeType.DARK:
            return self.variants[4]
        return self.variants[0]

    @property
    def hex(self) -> str:
        return self.base.hex

    def index(self, color: Color) -> int | None:
        # returns 0 if the color is this family's base, 1-5 if it's a variant, or None if it doesn't appear in this family.
        if color == self.base:
            return 0
        if color in self.variants:
            idx = self.variants.index(color)
            return idx + 1
        return None

    def __eq__(self, other: ColorFamily) -> bool:
        if not isinstance(other, ColorFamily):
            return False
        return (
            self.base == other.base
            and self._light == other._light
            and self._dark == other._dark
            and self._scheme_type == other._scheme_type
            and tuple(self.variants) == tuple(other.variants)
        )

    def __hash__(self):
        return hash(
            (
                self.base,
                tuple(self.variants),
                self._light,
                self._dark,
                self._scheme_type,
            )
        )


class ColorScheme:

    __ALIAS_COLORS = {
        # (start, end, centre)
        "red":     (345, 30,  20),
        "orange":  (30,  65,  50),
        "yellow":  (65,  110, 90),
        "green":   (110, 175, 142),
        "cyan":    (175, 220, 195),
        "blue":    (220, 280, 255),
        "purple":  (280, 340, 315),
        "magenta": (315, 355, 335),
    }

    __DISTINCT_THRESHOLD = 15

    def __init__(self, scheme: dict, scheme_type: SchemeType | str):
        # scheme dict should contain "foreground", "background", and "accents". It may also contain "surfaces"

        self._colors = None
        self._aliases = {}
        self._distinct = None

        if not isinstance(scheme_type, SchemeType):
            scheme_type = SchemeType[scheme_type.upper()]

        if scheme_type == SchemeType.EMPTY:
            self._accents = None
            self._foreground = None
            self._background = None
            self._scheme_type = SchemeType.EMPTY
            self._surfaces = None
            self._auto_surface = None
            return

        self._scheme_type = scheme_type
        self._accents = []
        self._surfaces = []

        # Verify scheme dict structure
        for key in ["foreground", "background", "accents"]:
            if key not in scheme:
                raise KeyError(f'Scheme must contain a "{key}" key.')

        for key in ["foreground", "background"]:
            if not isinstance(scheme[key], str):
                raise ValueError(
                    f'scheme["{key}"] must be a single hex string, not {type(scheme[key])}'
                )

        if not isinstance(scheme["accents"], list):
            raise ValueError(
                f'scheme["accents"] must be a list of hex strings, not {type(scheme["accents"])}'
            )

        for v in scheme["accents"]:
            if not isinstance(v, str):
                raise ValueError(
                    f'scheme["accents"] must be a list of hex strings, not a list of {type(v)}'
                )

        surfaces = scheme.get("surfaces")
        if surfaces is not None and not isinstance(surfaces, list):
            raise ValueError(
                f'If provided, scheme["surfaces"] must be a list of hex strings, not {type(surfaces)}'
            )
        if surfaces is not None:
            for s in surfaces:
                if not isinstance(s, str):
                    raise ValueError(
                        f'If provided, scheme["surfaces"] must be a list of hex strings, not a list of {type(s)}'
                    )

        foreground = Color(scheme["foreground"])
        background = Color(scheme["background"])

        # make sure we have a dark foreground on a light background if it's a light scheme, or vice versa for a dark scheme
        if self._scheme_type == SchemeType.LIGHT:
            if background.is_darker_than(foreground):
                foreground, background = background, foreground
        else:
            if foreground.is_darker_than(background):
                foreground, background = background, foreground

        self._foreground = ColorFamily(
            foreground, self._scheme_type, background, foreground, True
        )
        self._background = ColorFamily(
            background, self._scheme_type, background, foreground, True
        )

        for color in scheme["accents"]:
            self._accents.append(
                ColorFamily(
                    Color(color),
                    self._scheme_type,
                    background,
                    foreground,
                    False,
                )
            )

        if surfaces is not None:
            for surface in surfaces:
                self._surfaces.append(
                    ColorFamily(
                        Color(surface),
                        self._scheme_type,
                        background,
                        foreground,
                        False,
                    )
                )

        self._surfaces.sort(
            key=lambda c: c.base.oklab.l, reverse=self._scheme_type == SchemeType.DARK
        )

        self._aliases = self.determine_aliases()

        # List of accent colours excluding any that are too similar to other accents
        self._distinct_accents = [self._accents[0]]

        distances = {}
        for color1 in self._accents:
            distances[color1] = {}
            for color2 in self._accents:
                distances[color1][color2] = color1.base.distance_to(color2.base)

        while len(self._distinct_accents) < len(self._accents):
            next_color = max(
                self._accents,
                key=lambda c: min(distances[c][d] for d in self._distinct_accents),
            )
            dist = min(distances[next_color][d] for d in self._distinct_accents)
            if dist < self.__DISTINCT_THRESHOLD:
                break
            self._distinct_accents.append(next_color)

        # Re-order back to accent color order. If the user wants them in contrast order, they should use ColorScheme.high_contrast()
        self._distinct_accents = [
            c for c in self._accents if c in self._distinct_accents
        ]

        self._auto_surface = self._generate_auto_surface()

        # TODO: Maybe choose more appropriate lightness for the base color if the accents are not suitable

    @staticmethod
    def _circular_hue_diff(h1: float, h2: float) -> float:
        return abs((h1 - h2 + 180) % 360 - 180)

    @classmethod
    def _in_hue_range(
        cls, h: float, h_min: float, h_max: float, tol: float = 1e-5
    ) -> bool:
        # This should be order independent for h_min and h_max
        # handles h < 0 and h > 360 properly
        # Always evaluates based on the *minor* arc

        d_bounds = cls._circular_hue_diff(h_min, h_max)
        d_to_min = cls._circular_hue_diff(h_min, h)
        d_to_max = cls._circular_hue_diff(h, h_max)

        return (d_to_min + d_to_max) <= d_bounds + tol

    @classmethod
    def _dist_to_hue_range(
        cls, h: float, h_min: float, h_max: float, tol: float = 1e-5
    ) -> float:
        # Returns 0 if it's within the range

        d_bounds = cls._circular_hue_diff(h_min, h_max)
        d_to_min = cls._circular_hue_diff(h_min, h)
        d_to_max = cls._circular_hue_diff(h, h_max)
        
        if (d_to_min + d_to_max) <= d_bounds + tol:
            return 0.0

        return min(d_to_min, d_to_max)

    @classmethod
    def _alias_cost(
        cls,
        accent: Color,
        h_min: float,
        h_max: float,
        h_centre: float,
        target_c: float,
        target_l: float,
        w_l: float = 10.0,
        w_c: float = 15.0,
        outside_penalty: float = 50.0,
    ) -> float:
        acc_lch = accent.oklch
        h = acc_lch.h

        d_to_range = cls._dist_to_hue_range(h, h_min, h_max)
        if d_to_range == 0.0:
            # we're inside the acceptable range. 
            # Cost should be very small, decreasing the closer we are to the "centre" 
            hue_cost = cls._circular_hue_diff(h, h_centre) / 20.0
        else:
            # we're outside the acceptable range. Big cost penalty, plus even more 
            # penalty by distance
            hue_cost = outside_penalty + d_to_range

        # small contribution from lightness and chroma differences
        dl = abs(acc_lch.l - target_l)
        lightness_cost = dl * w_l

        dc = abs(acc_lch.c - target_c)
        chroma_cost = dc * w_c

        return hue_cost + lightness_cost + chroma_cost

    def determine_aliases(self) -> dict[str, ColorFamily]:
        reuse_penalty = 15.0
        background_compensation = 0.2
        bg_oklab = self._background.base.oklab

        cost_matrix: dict[str, dict[Color, float]] = {}

        for alias_name, (h_min, h_max, h_centre) in self.__ALIAS_COLORS.items():

            cost_matrix[alias_name] = {}
            for accent in self._accents:
                cost_matrix[alias_name][accent.base] = self._alias_cost(
                    accent=accent.base,
                    h_min=h_min,
                    h_max=h_max,
                    h_centre=h_centre,
                    target_c = 0.5,
                    target_l = 0.5,
                )

        # High-confidence aliases resolve first
        aliases_by_confidence = sorted(
            self.__ALIAS_COLORS.keys(),
            key=lambda alias: min(cost_matrix[alias].values()),
        )

        assigned_counts: Counter[ColorFamily] = Counter()
        resolved: dict[str, ColorFamily] = {}

        for alias_name in aliases_by_confidence:
            best_accent = min(
                self._accents,
                key=lambda accent: cost_matrix[alias_name][accent.base]
                + (assigned_counts[accent] * reuse_penalty),
            )
            resolved[alias_name] = best_accent
            assigned_counts[best_accent] += 1

        return resolved


    def high_contrast(self, n: int) -> list[ColorFamily]:
        if n <= 0:
            return []
        if n == 1:
            return [self._accents[0]]
        if n >= len(self._accents):
            return self._accents.copy()

        # We want to find the set of n colours such that the minimum distance between any pair of colours is maximised.

        best_subset = None
        best_min_dist = -1

        # For each combination of n colors:
        for subset in combinations(self._accents, n):

            # find the minimum distance between any two colours in this subset
            min_dist = min(
                c1.base.distance_to(c2.base) for c1, c2 in combinations(subset, 2)
            )

            if min_dist > best_min_dist:
                best_min_dist = min_dist
                best_subset = list(subset)

        return best_subset or self._accents[:n]

    def _generate_auto_surface(self) -> ColorFamily:
        bg_color = self.background.base
        bg_oklch = bg_color.oklch
        dark_scheme = self._scheme_type == SchemeType.DARK

        target_l = 0 if dark_scheme else 1
        headroom = abs(target_l - bg_oklch.l)

        # If we have no headroom (i.e, starting from pure white or black), we'll flip direction.
        # This means things will be similar to background.variants
        if headroom < 0.08:
            target_l = 0.2 if dark_scheme else 0.85
            headroom = abs(target_l - bg_oklch.l)

        chroma = bg_oklch.c
        hue = bg_oklch.h

        # If background has no chroma, infuse a little from foreground.
        # If that's *also* achromatic, try first accent color
        if chroma < 0.01:
            if self.foreground.base.oklch.c > 0.02:
                hue = self.foreground.base.oklch.h
                chroma = 0.015
            elif self.accents[0].base.oklch.c > 0.02:
                hue = self.accents[0].base.oklch.h
                chroma = 0.015
            # Could be an achromatic palette, so we'll give up here

        # We'll have 5 variants + the base from 15% to 85% of the available headroom
        variants = []
        step_fractions = [(i + 1) / 7 for i in range(6)]

        for t in step_fractions:
            new_l = bg_oklch.l + (target_l - bg_oklch.l) * t
            # reduce chroma to hopefully avoid unpleasant RGB clipping near lightness extremes
            new_c = chroma * (1 - 0.5 * t)

            surface_color = Color(OKLCH(new_l, new_c, hue))
            variants.append(surface_color)

        variants.sort(key=lambda c: self._background.base.distance_to(c))

        return ColorFamily(
            variants[0],
            self._scheme_type,
            self.foreground.base if dark_scheme else self.background.base,
            self.background.base if dark_scheme else self.foreground.base,
            is_main=False,
            variants=variants[1:][::-1],
        )

    @property
    def foreground(self) -> ColorFamily:
        return self._foreground

    @property
    def background(self) -> ColorFamily:
        return self._background

    @property
    def accents(self) -> list[ColorFamily]:
        return self._accents

    @property
    def surfaces(self) -> list[ColorFamily]:
        return self._surfaces

    @property
    def auto_surface(self) -> list[ColorFamily]:
        return self._auto_surface

    @property
    def aliases(self) -> dict[str, ColorFamily]:
        return self._aliases

    @property
    def red(self) -> ColorFamily:
        return self._aliases["red"]

    @property
    def orange(self) -> ColorFamily:
        return self._aliases["orange"]

    @property
    def yellow(self) -> ColorFamily:
        return self._aliases["yellow"]

    @property
    def green(self) -> ColorFamily:
        return self._aliases["green"]

    @property
    def cyan(self) -> ColorFamily:
        return self._aliases["cyan"]

    @property
    def blue(self) -> ColorFamily:
        return self._aliases["blue"]

    @property
    def purple(self) -> ColorFamily:
        return self._aliases["purple"]

    @property
    def magenta(self) -> ColorFamily:
        return self._aliases["magenta"]

    @property
    def error(self) -> ColorFamily:
        return self.red

    @property
    def warning(self):
        # Usually yellow, but this can often be the same as green in which case we should return orange; better a warning be accidentally red than green
        if self.yellow == self.green:
            return self.orange
        return self.yellow

    @property
    def success(self):
        return self.green

    @property
    def info(self):
        return self.blue

    def get_canonical_name(
        self, color_family: ColorFamily
    ) -> tuple[str, int | None] | None:
        if self.foreground == color_family:
            return "foreground", None

        if self.background == color_family:
            return "background", None

        for i, accent in enumerate(self.accents):
            if accent == color_family:
                return "accents", i

        for i, surface in enumerate(self.surfaces):
            if surface == color_family:
                return "surfaces", i

        if self.auto_surface == color_family:
            return "auto_surface", None
