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
        force_variants: bool = False,
        is_main: bool = False,
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

        # We check if the base colour is too dark to have darker variants, or too light to have lighter variants
        too_light = not force_variants and (
            self._base.oklab.l / self._light.oklab.l > 0.9
        )
        too_dark = not force_variants and (
            self._base.oklab.l / self._dark.oklab.l < 0.2
        )

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

    def __getitem(self, index: int) -> Color:
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


class ColorScheme:

    # Mostly from Sturges and Whitfield, https://doi.org/10.1002/col.5080200605
    __ALIAS_COLORS = {
        "red": OKLCH(0.60, 0.22, 29),
        "orange": OKLCH(0.70, 0.18, 55),
        "yellow": OKLCH(0.88, 0.16, 103),
        "green": OKLCH(0.68, 0.18, 142),
        "cyan": OKLCH(0.75, 0.14, 195),
        "blue": OKLCH(0.50, 0.18, 264),
        "purple": OKLCH(0.52, 0.22, 305),
        "magenta": OKLCH(0.62, 0.24, 335),
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
            self._auto_surfaces = None
            return

        self._scheme_type = scheme_type
        self._accents = []
        self._surfaces = []
        self._auto_surfaces = []

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

        if "surfaces" in scheme:
            surfaces = scheme["surfaces"]
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
            foreground, self._scheme_type, background, foreground, False, True
        )
        self._background = ColorFamily(
            background, self._scheme_type, background, foreground, False, True
        )

        for color in scheme["accents"]:
            self._accents.append(
                ColorFamily(
                    Color(color),
                    self._scheme_type,
                    background,
                    foreground,
                    False,
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
                        False,
                    )
                )

        self._surfaces.sort(
            key=lambda c: c.base.oklab.l, reverse=self._scheme_type == SchemeType.DARK
        )

        self._aliases = self.determine_alises() 

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
                key=lambda c: min(distances[c][d] for d in self._distinct_colors),
            )
            dist = min(distances[next_color][d] for d in self._distinct_colors)

            if dist < self.__DISTINCT_THRESHOLD:
                break

        # Re-order back to accent color order. If the user wants them in contrast order, they should use ColorScheme.contrast()
        self._distinct_accents = [c for c in self._accents if c in self._distinct_accents]

        # TODO: Maybe choose more appropriate lightness for the base color if the accents are not suitable

    def determine_alises(self):
        reuse_penalty = 12

        bg_oklab = self._background.oklab

        background_compensation = 0.2

        assigned_counts = Counter()
        resolved = {}

        cost_matrix = {}
        for alias_name, target in self.__ALIAS_COLORS.items():
            # Include a small compensation for the perceptual shift due to the background hue.
            # Instead of changing the accent color, we'll shift the target in the opposite direction
            target_l = target.oklab.l
            target_a = target.oklab.a + bg_oklab.a * background_compensation
            target_b = target.oklab.b + bg_oklab.b * background_compensation
            target = OKLAB(target_l, target_a, target_b)
            for accent in self._accents:
                cost_matrix[alias_name][accent.base] = accent.distance_to(target)

        aliases_by_confidence = sorted(
            self.__ALIAS_COLORS.keys(),
            key=lambda alias: min(cost_matrix[alias].values()),
        )

        for alias_name in aliases_by_confidence:
            best_accent = min(
                self._accents,
                key=lambda accent: cost_matrix[alias_name][accent.base]
                + (assigned_counts[accent] * reuse_penalty),
            )
            resolved[alias_name] = best_accent
            assigned_counts[best_accent] += 1

    def high_contrast(self, n: int) -> list[ColorFamily]:
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

