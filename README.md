# Pygmentation

[![Ruff](https://img.shields.io/github/actions/workflow/status/ech0-chambers/pygmentation/ci.yml?branch=main&job=lint&label=ruff)](https://github.com/ech0-chambers/pygmentation/actions/workflows/ci.yml) [![Mypy](https://img.shields.io/github/actions/workflow/status/ech0-chambers/pygmentation/ci.yml?branch=main&job=typecheck&label=mypy)](https://github.com/ech0-chambers/pygmentation/actions/workflows/ci.yml) [![Tests](https://img.shields.io/github/actions/workflow/status/ech0-chambers/pygmentation/ci.yml?branch=main&job=test&label=tests)](https://github.com/ech0-chambers/pygmentation/actions/workflows/ci.yml)

A colour manipulation and palette generation package with optional Matplotlib integration. For full API documentation, see [the docs](https://ech0-chambers.github.io/pygmentation).

![The Nord dark colour scheme rendered by Pygmentation.](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/nord.svg)

------------------------------------------------------------------------

## Contents

- [Capabilities at a Glance](#capabilities-at-a-glance)
- [Colour Aliases](#colour-aliases)
- [Motivation](#motivation)
- [Colour Theory & Mathematical Foundations](#colour-theory-mathematical-foundations)
- [Requirements & Installation](#requirements-installation)
- [Quickstart](#quickstart)
- [Python Library Guide](#python-library-guide)
- [Command-Line Interface](#command-line-interface)
- [Output Formats Reference](#output-formats-reference)
- [Custom Schemes & Extensibility](#custom-schemes-extensibility)
- [Development & Quality Gates](#development-quality-gates)

------------------------------------------------------------------------

## Capabilities at a Glance

- Sophisticated handling of colours, colour models/spaces and their conversions, and colour manipulations
- Context-aware generation of tints and shades, ensuring colour variants are harmonious with the foreground/background colours
- Full palette generation from a handful of base colours -- only a foreground, background, and one or more accent colours are needed
- Highly consistent naming and structure across schemes -- specifying colours by their position in the scheme (e.g. `Accent 1`) allows projects to easily take on the "vibe" of a particular palette, while semantic aliases like `Blue` or `Error` allow deliberate use of colours to communicate meaning
- Consistent contrast across light and dark themes -- a colour variant with good contrast to the background will maintain that contrast regardless of the scheme, in both light and dark themes
- Exporters for common formats, including LaTeX, CSS, JavaScript, and less.js, with an easily extensible base class for custom exporters
- Direct integration with Matplotlib to apply consistent styling across plots, with significant font handling capabilities

### Scheme Overview

All schemes must have at least a foreground colour, a background colour, and at least one (usually six or more) accent colour. Some may also define any number of surface colours, though these are optional. In a light scheme, the background colour must be lighter than the foreground, and vice versa for a dark scheme.

Each colour in the scheme receives 5 variants, which are lighter/darker variants generated in a way that keeps them harmonious with the rest of the colour scheme. For details on this generation, see [Variant Derivation](#variant-derivation). Together with the base colour, these are known collectively as a colour family. A colour family's variants are ordered by their contrast to the background colour, from most contrast to least contrast. Usually, the base colour will sit between variant 2 and variant 3, though this is not always the case. As an example, the dark theme for the [Nord colour scheme](https://www.nordtheme.com/) is shown below, with its variant colours.

![The Nord dark colour scheme rendered by Pygmentation.](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/nord.svg)

------------------------------------------------------------------------

## Colour Aliases

While colours can always be accessed by their position in the scheme (e.g, `var(--clr-accent1)` in the CSS output), semantic aliases (red, orange etc) are automatically identified by matching accent colours to canonical hue targets in Oklch space. Matches are determined globally, which allows a small adjustment to discourage multiple aliases mapping to the same colour. The target hues and acceptable ranges are defined as follows:

![OKLCh reference hue ranges and target angles for semantic colour aliases](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/reference_colors.svg)

In addition, four functional aliases are mapped:

- **`error`**: maps to `red`
- **`warning`**: maps to `yellow` (or sometimes `orange`, if `yellow` is the same as `green` which can happen in some schemes)
- **`success`**: maps to `green`
- **`info`**: maps to `blue`

Every alias is resolved to the nearest accent colour using Oklch hue proximity and Oklab distance. It is possible for multiple aliases to map to the same colour, for example in the Nord scheme `magenta` and `purple` both map to the same colour.

------------------------------------------------------------------------

## Motivation

I first started this library because I wanted a way to make my plots and diagrams visually consistent with the rest of my LaTeX documents, particularly with the ability to swap colour schemes easily and consistently. Over time, I iterated on this package, adding more features and improving the colour handling whenever I found the output to be subpar. The result is that this package provides excellent handling of a variety of colour models, manipulations of those colours, and extrapolating pleasing palettes from a scheme's fundamental base colours with a consistent API and naming scheme applicable across several output formats, including LaTeX, CSS, JavaScript, and Textual.

Below are a few of the problems that this package aims to solve.

### sRGB and HSL Issues

Representing a colour as three integers for red, green, and blue intensity is helpful in computer graphics because it directly mirrors the way that most displays show colour; each pixel consists of a red, green, and blue subpixel which can be lit with an intensity ranging from 0 to 255, positioned close enough together to trick the eye into seeing them as a single colour. This display method works reasonably well, and so integer RGB values are a good way to represent colours when they are being sent to a screen for display, but it falls short in describing colour as we experience it.

Firstly, using integers restricts the number of possible colours to a finite set (admittedly a large set of nearly 17 million, but still finite). There are also many colours we can see which cannot be expressed in sRGB since they fall outside the range of 0 to 255 in one or more of the channels. sRGB covers only about 35% of the colours humans can see. Additionally, the "perceptual distance" (how different two colours appear to be) is not uniform throughout the sRGB colour space. Taking a colour and adding 10 to the red value, 5 to the green value, and 20 to the blue value might produce a new colour that is very different from the original, or almost indistinguishable, depending on what the original colour was.

Of course, this is fine if all you want to do is specify the colour of something on a screen; this will get converted to sRGB anyway to send to the display. The problems arise when you want to manipulate the colour first. It's quite possible for a colour transformation to take a colour outside the range of possible RGB values, then for another transformation to bring it back inside. If colour is only expressed as RGB values, this sequence of transformations breaks; even if we take the "closest" RGB colour after the first transformation, the second transformation is now acting on a completely different colour.

Colour manipulations themselves are also tricky. If I have a particular shade of blue that I like, but I want to use a pastel version of it for a background, it's not particularly obvious how to find that pastel blue from the RGB representation. RGB is also not an intuitive way for us to think about colour. If you were presented with the hex code `#135C55`, you're unlikely to know intuitively that it's a deep teal (![#135C55](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_1.svg)). You're even more unlikely to know that it has the same hue as `#E1F5F3`.

To combat this, another colour model is often used, HSL, where colours are expressed as a hue angle (0° being pure red), a saturation from 0% (greyscale) to 100%, and a lightness from 0% (black) to 100% (white). This allows for easy answers for things like "I want this colour, but 20% lighter", but still has all the same pitfalls as RGB since it's just a different way to express the same colours. Although this makes transformations easier, they're still inaccurate. If we start with a pure blue colour, ![#0000FF](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_2.svg), and increase the lightness while reducing the saturation, we get ![#CFCFFC](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_3.svg). This has clearly shifted slightly towards purple, despite ostensibly having the same pure blue hue of 240°.

### Consistency Across Formats

If you work with multiple tools and formats, even if you use the same base colour palette, each tool will likely handle it differently, resulting in images or documents which *almost* match but don't quite. It's difficult to keep every tool in sync with each other if the scheme is updated. Switching between light and dark modes can also be problematic, as can changing schemes entirely. As well as aesthetics, you may want to use colour to convey meaning, such as using red to report errors or green to indicate success. This can also cause conflicts when swapping colour schemes (either as a developer, or if the user can select a scheme), as elements whose colour was chosen for semantic reasons may have that colour (and its connotations) changed, or else aesthetic choices may be forced to change to maintain the semantic colours.

Contrast within themes is a particularly overlooked issue. Creating accessible interfaces involves maintaining good contrast between text, page furniture/ornaments, and backgrounds. Colours (and particularly variants of colours) chosen for a dark scheme will often be wholly inappropriate for a light scheme. This normally means double the work; choosing a set of colours to match the light theme and a separate set entirely for the dark theme.

------------------------------------------------------------------------

### Pygmentation's Solution

`pygmentation` attempts to address all of these problems. Colours are stored internally in the Oklab colour space which is perceptually uniform (colour modifications produce a consistent visual difference regardless of the starting colour), covers the entire range of colours humans can perceive and (infinitely) more (so no unexpected clipping when a colour channel goes out of bounds), and doesn't suffer from any hue drift when changing the lightness or saturation of a colour. All colour manipulations happen in this colour space, producing very consistent, pleasing results which are then converted to RGB to be passed to whatever tools you use (CSS, LaTeX, matplotlib etc). This maintains a single source of truth for the palette, and keeps all colour manipulations correctly handled in one place so that different tools don't have chance to deviate.

Each scheme has a number of accent colours, from which semantic colour aliases are found; you can access colours by their number (Accent 1 etc), by name (red, magenta, blue etc), or by their typical function (error, success, info etc). This makes changing scheme incredibly easy, with most schemes being a drop-in replacement. Five variants of each colour are generated in a context-aware fashion, and always ordered from most contrast with the background to least. This again makes swapping from a dark theme to a light theme an absolute breeze. Instead of asking your software for a light blue, you ask for a blue with good contrast to the text colour, or a red with good contrast to the background colour. If the theme is ever inverted, contrast is maintained as colours adjust to keep the same relationships in an aesthetically pleasing way.

------------------------------------------------------------------------

## Colour Theory & Mathematical Foundations

To appreciate how `pygmentation` derives its colour families, it is helpful to examine the colour science that underpins the package.

### Why Geometric Colour Spaces Fail Human Vision

Human vision does not perceive light linearly; the human eye is far more sensitive to green wavelengths than to deep blue or deep red. Because the RGB and HSL models are coordinate representations based on display hardware, all colour channels are treated symmetrically.

Furthermore, geometric models do not account for the Helmholtz-Kohlrausch effect, in which vivid, highly saturated colours are perceived as brighter than muted colours of identical physical luminance -- a saturated yellow light is perceived as brighter than a white light.

When "lightness" is altered in HSL, a linear calculation is performed on a non-linear perceptual space. This results in visual inconsistency: adjusting two different colours by the same "20% lightness" produces two noticeably different changes in perceived brightness.

For example, we may start from a pure blue and a pure yellow, and lighten both by 20% in HSL. For blue, this produces a noticeable change: ![Comparison of #0000FF and #6666FF](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_4.svg). For yellow, however, the difference is nearly negligible, if anything appearing slightly washed out instead of lightened: ![Comparison of #FFFF00 and #FFFF66](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_5.svg). In darker tones, the difference is reversed with yellow showing a larger change than blue when darkened by 20%: ![Comparison of #0000FF and #000099](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_6.svg) compared to ![Comparison of #FFFF00 and #999900](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_7.svg).

### Perceptual Uniformity: CIEDE2000 and Oklab / Oklch

A perceptually uniform colour model is one in which a given change in coordinates produces the same visual change, regardless of the starting position. To put things more mathematically, if a starting colour $\vec{C}$ is shifted by some $\vec{t}$ to give a new colour $\vec{C^\prime} = \vec{C} + \vec{t}$, then the visual difference between $\vec{C}$ and $\vec{C^\prime}$ is always the same, no matter what $\vec{C}$ was.

Neither RGB nor HSL are perceptually uniform. In terms of lightness, this is made clear by the comparison of yellow and blue above. For hue, this is readily demonstrated by comparing the perceived difference between two green hues and two blue hues separated by an identical $30^\circ$ angle in HSL:

- Green at $100^\circ$ and $130^\circ$: ![Comparison of #55FF00 and #00FF2B](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_8.svg).
- Blue at $260^\circ$ and $290^\circ$: ![Comparison of #5500FF and #D500FF](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/swatch_9.svg).

Although both pairs are separated by exactly $30^\circ$ on the HSL colour wheel, the two greens appear nearly indistinguishable, whereas the blue and purple represent a striking visual leap.

#### The CIEDE2000 Benchmark

In 1976, the International Commission on Illumination introduced the CIELAB ($L^*a^*b^*$) colour space. It maps colours on a scale of lightness (0 to 100), $a$ which represents green to red, with negative values more green and positive more red, and $b$ in which negative values are blue and positive values are yellow. It was intended to be perceptually uniform, based on human observations of colour under specific reference conditions. While a substantial improvement over RGB, CIELAB still exhibits perceptual distortions, particularly in blue and violet shades.

To address these shortcomings, the CIEDE2000 ($\Delta E_{00}$) colour difference formula was introduced. Rather than computing a simple geometric distance, CIEDE2000 applies several corrections:

- Weighting functions which account for differences in sensitivity depending on the lightness, chroma, and hue.
- A rotation term to correct for distortion in the blue-violet region.
- A neutral-grey adjustment to improve accuracy for desaturated pastels.

The full CIEDE2000 algorithm is implemented in `Color.distance_to_CIEDE2000()`, providing an established benchmark for colour distance.

It should be noted, however, that this formula is only intended for evaluating differences between similar colours. The CIEDE2000 specification suggests that it should only be used for colours with a $\Delta E \leq 5$, since some of its assumptions break down when colours are far apart (in particular, it assumes that both colours' local space is similar to the local space of their midpoint, which may not be the case for vastly different colours).

#### Oklab and Oklch (Ottosson, 2020)

While CIEDE2000 is an excellent distance metric for short distances, it is computationally intensive and cannot be inverted easily for colour manipulation (it is a correction applied to a perceptually non-uniform colour space, rather than a transformation from that space to one which is perceptually uniform).

In 2020, Björn Ottosson published Oklab, a perceptual colour space designed using experimental data on human colour perception (see <https://bottosson.github.io/posts/oklab/>). Like CIELab, Oklab represents colours as a lightness, $a$ (red-green dimension), and $b$ (blue-yellow dimension). It is much closer to being perceptually uniform, so much so that the Euclidean distance between colours is sufficient to replace the computationally expensive CIEDE2000 calculation.

When transformed into polar coordinates, this space is referred to as Oklch:

- $L$: Perceptual lightness.
- $C = \sqrt{a^2 + b^2}$: Perceptual chroma (a concept similar to saturation).
- $h = \text{atan2}(b, a)$: Hue angle in degrees ($0^\circ \le h < 360^\circ$).

Oklab eliminates the hue-shifting issues seen in CIELAB and HSL: altering lightness in Oklab does not cause blue hues to drift into purple. Within `pygmentation`, Oklab and Oklch are used for the canonical "true" values of colours. All colour manipulations happen in Oklab and Oklch space, and colours are stored and compared by their Oklab values, converting to other colour models for output or model-specific manipulations.

------------------------------------------------------------------------

### Consistent Contrast

Colour schemes in `pygmentation` are intended to be as close to drop-in replacements for each other as possible, regardless of the number of colours, colour order, and light/dark theming. This makes it vitally important that colours which have good contrast in one theme also have good contrast in another. Of course, this is very hard to enforce between accent colours without imposing restrictions on the colour schemes. However, we can ensure that contrast against the background and foreground colours is consistent. Within each colour family, the variants are always ordered from most contrast with the background colour to least contrast with the background colour. Compare the images below for the Nord dark scheme and the Rose Pine Dawn light scheme.

![The Nord dark colour scheme rendered by Pygmentation.](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/nord.svg)

![The Rose Pine Dawn light colour scheme rendered by Pygmentation.](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/rose_pine_dawn.svg)

------------------------------------------------------------------------

### Variant Derivation

Each base colour in a scheme forms a `ColorFamily` consisting of the base colour itself and five systematically derived variants.

#### Directional Lightness Scaling

Variants are calculated by scaling lightness in Oklab space. In standard cases, variants are generated using fractional adjustments:

- In a **light scheme**, variants are 50% and 25% darker, and 40%, 60%, and 80% lighter.
- In a **dark scheme**, the directions are inverted: variants are 50% and 25% lighter, and 40%, 60%, and 80% darker.

Here, "20% lighter" doesn't mean that the lightness is increased by 20%. Instead, it means that the lightness is increased to be 20% closer to full lightness. In other words, a colour with lightness $l$ which is lightened by some amount $p < 1$ has final lightness $l^\prime = l + (1 - l) \times p$. For darkening by an amount $p < 1$, $l^\prime = l \times (1 - p)$. In fact, in `pygmentation` schemes, the maximum and minimum lightness is usually that of the background/foreground colours instead of 1 and 0, keeping variants context-aware so that they can never become lighter/darker than the foreground/background colours.

There are exceptions and adjustments to these general rules, which form the rest of this section.

#### Contrast Bounds Clamping

To prevent lighter variants from washing out into a light background, and darker variants from collapsing into a dark background, the target lightness is clamped. For darkening, the target lightness cannot be below 0.2, and for lightening it cannot be above 0.8.

#### Extreme Base Colours and Array Inversion

If a base colour has an extreme lightness, generating variants in the same way is significantly less useful. A very light base colour in a dark theme would result in the base colour and three lighter variants being almost indistinguishable, while the two darker variants represent huge visual jumps. Determining whether a colour is "too light" or "too dark" is done by considering how extreme its lightness is compared to the foreground/background lightness. If $l_B$ and $l_F$ are the lightnesses of the background and foreground colours respectively (clamped as described above), then a colour with lightness $l$ is considered too light if $\frac{l - 0.5}{\max(l_F, l_B) - 0.5} > 0.8$, and too dark if $\frac{0.5 - l}{0.5 - \min(l_F, l_B)} > 0.8$. In other words, we ask "Compared to a pure mid-tone, is the colour at least 80% as light as the foreground/background colour? Compared to a pure mid-tone, is it at least 80% as dark as the foreground/background colour?", choosing between foreground and background based on whether we are considering a light or dark theme.

For base colours deemed too dark or too light for the normal variant generation, variants are produced which are 10%, 25%, 50%, 75%, and 90% lighter or darker. The order of these variants is reversed in a dark theme, to maintain the usual order of contrast with the background colour.

#### Fractional Chroma Blending

Changing only the lightness produces subpar results, with dark variants looking particularly out of place and oversaturated. To keep variants more harmonious with the foreground/background colours, the chroma of the base colour is also modified. A variant's chroma is shifted towards the chroma of the foreground/background colour by the same amount by which it is lightened/darkened, multiplied by an additional factor `chroma_blend`.

$$C_{\text{variant}} = C_{\text{base}} + (C_{\text{F or B}} - C_{\text{base}}) \times x \times C_{\text{blend}}$$

By default, `chroma_blend = 0.75`. This subtle shift prevents saturated accents from appearing unnatural on desaturated background, without appearing washed out if the background colour has high saturation. The sample below has this chroma blend disabled; the darker variants in particular stand out and are quite jarring.

![The Nord dark colour scheme with chroma blending disabled for variants.](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/nord_no_chroma.svg)

#### Ambient Hue Alignment

When a base colour's hue is already very close to the background or foreground anchor (within $30^\circ$ in Oklch), it can produce better results to subtly shift the hue as well. In this case, instead of lightening/darkening and adjusting the chroma, the variant is simply a linear interpolation between the original colour and the foreground or background colour, evaluated in Oklab space. Because the foreground and background are considered separately, it is possible (and likely) that a colour's lighter variants are directly lightened, while its darker variants are interpolated towards the foreground/background colour, or vice versa. Taking the Nord scheme as an example again, in the dark theme accent colours 1 and 3 exhibit this behaviour, linearly interpolating towards the background colour.

------------------------------------------------------------------------

## Requirements & Installation

`pygmentation` requires **Python \>= 3.11**.

Core package dependencies are strictly limited to `numpy` and `rich`. Matplotlib integration is packaged as an optional extra.

``` bash
# Core package (colour models, schemes, exporters, and CLI):
pip install pygmentation

# With Matplotlib publication styling and font discovery:
pip install "pygmentation[plots]"

# For development and testing (pytest, ruff, mypy):
pip install "pygmentation[dev]"
```

When installed, the `pygmentation` command-line executable is automatically added to your system `PATH`.

------------------------------------------------------------------------

## Quickstart

### Python Library

``` python
import pygmentation as pyg

# Load a colour scheme (variant can be "light" or "dark", or pyg.SchemeType)
scheme = pyg.get_scheme("nord", "dark")

# Access background and primary red accent
bg_color = scheme.background.base.hex         # "2E3440"
red_base = scheme.red.base.css                # "#BF616A"

# Access variants (Variant 1 is highest contrast against background)
red_high_contrast = scheme.red[1].css         # "#D7848A"

# Seamlessly convert to other colour models
r, g, b = scheme.red.base.rgb.as_255          # (191, 97, 106)
l, a, b = scheme.red.base.oklab               # (0.573, 0.134, 0.059)
```

### Command-Line Interface

Write a colour scheme to a file (see section [`write`](#write)):

``` bash
pygmentation write nord dark -f nord.css
```

Display any colour scheme in your terminal with rich full-colour swatches:

``` bash
pygmentation show nord dark
```

![pygmentation show nord dark](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/terminal_1.svg)

------------------------------------------------------------------------

## Python Library Guide

The top-level namespace provides access to all core classes, functions, and the scheme registry:

``` python
from pygmentation import (
    get_scheme,
    list_schemes,
    Color,
    ColorScheme,
    ColorFamily,
    SchemeType,
    registry,
)
```

### Loading Colour Schemes

Schemes are loaded on demand via `get_scheme()`:

``` python
# Pass scheme name and variant as strings:
nord_dark = get_scheme("nord", "dark")
nord_light = get_scheme("nord", "light")

# Or use the SchemeType enum:
catppuccin = get_scheme("catppuccin", SchemeType.DARK)

# Discover all available schemes:
names = list_schemes()
```

### The `ColorScheme` Object

A `ColorScheme` contains the complete set of colour families:

- **Standard Families:**
  - `scheme.foreground`: The foreground colour family.
  - `scheme.background`: The background colour family.
  - `scheme.accents`: A list of all accent colour families (`list[ColorFamily]`).
  - `scheme.surfaces`: A list of explicitly defined surface colour families (may be empty).
  - `scheme.auto_surface`: An automatically synthesised surface colour family balancing contrast and background tint.
- **Semantic Aliases:**
  - `scheme.red`, `scheme.orange`, `scheme.yellow`, `scheme.green`, `scheme.cyan`, `scheme.blue`, `scheme.purple`, `scheme.magenta`.
  - Functional roles: `scheme.error`, `scheme.warning`, `scheme.success`, `scheme.info`.
- **Distinct Accents:**
  - `scheme.distinct`: Returns a list of accent colour families with similar colours filtered out. This is in the same order as `scheme.accents`.
  - `scheme.high_contrast(n)`: Fetch the `n` accent colours which collectively are as different as possible.
- **Iteration:**
  - Iterating over a scheme yields all colour families (foreground, background, accents, surfaces, and auto-surface).

### The `ColorFamily` Object

A `ColorFamily` encapsulates a base colour and its five derived variants:

- **Variant Access:**
  - `family.base`: The underlying base `Color` object.
  - `family[0]`: Equivalent to `family.base`.
  - `family[1]` through `family[5]`: The five contrast-ordered variant `Color` objects.
  - `ColorFamily` instances are iterable and can be used in list unpacking. `base, *variants = family` will work as expected.
  - `family.lightest`: Returns the variant with the highest Oklab lightness.
  - `family.darkest`: Returns the variant with the lowest Oklab lightness.

### The Immutable `Color` Value Object

The `Color` class represents a single colour. It is implemented as a frozen, immutable value object; methods never modify the existing instance in place, but instead return a new `Color`. Therefore, it is hashable and safe to use for dictionary keys.

``` python
c = Color("#BF616A")
unmodified = Color("#BF616A")

# Transformations (all return new Color instances):
lighter = c.lighten(0.20)              # Lighten by 20% in Oklab
darker = c.darken(0.15)                # Darken by 15% in Oklab
blended = c.lerp(Color("#88C0D0"), 0.5) # Linear interpolation in Cartesian Oklab
channel_mod = c.with_r(0.8)            # Channel modification

assert c == unmodified                 # The Color object has not been mutated
```

#### Colour Model Conversions

Every `Color` object exposes properties that compute representations in seven colour models on demand:

``` python
c = Color("#BF616A")

c.rgb      # RGB model (normalized floats 0.0 - 1.0)
c.hsl      # HSL model (h in degrees, s and l in 0.0 - 1.0)
c.hsv      # HSV model (as for HSL)
c.xyz      # CIE XYZ model (0.0 - inf)
c.lab      # CIELAB model (l in 0.0 - 100, a and b unbounded)
c.oklab    # Oklab model (l in 0.0 - 1.0, a and b unbounded)
c.oklch    # Oklch model (l in 0.0 - 1.0, c chroma 0.0 - inf, h in degrees)

# Integer RGB access:
c.as_255       # Returns an _RGB_255 named tuple instance: (191, 97, 106)
c.as_255.r     # 191
c.as_255.g     # 97
c.as_255.b     # 106

# String formatting:
c.hex          # "BF616A" (uppercase 6-character hex without '#')
c.css          # "#BF616A" (with leading '#')
```

#### Perceptual Comparisons & Distances

``` python
c1 = Color("#BF616A")
c2 = Color("#5E81AC")

# Euclidean distance in Oklab space (fast and perceptually uniform):
dist = c1.distance_to(c2)

# Full CIEDE2000 distance in CIELAB (intended for comparison of similar colours):
delta_e = c1.distance_to_CIEDE2000(c2)

# Hue differences:
dh_hsl = c1.hue_diff(c2)           # HSL hue difference in degrees (-180 to 180)
dh_ok = c1.hue_diff_oklch(c2)      # Oklch hue difference in degrees

# Lightness comparisons (in Oklab):
is_darker = c1.is_darker_than(c2)
is_lighter = c1.is_lighter_than(c2)
```

------------------------------------------------------------------------

### Matplotlib Publication Styling

With the `[plots]` extra installed, `pygmentation.plot` configures Matplotlib's `rcParams` to match your chosen colour scheme for publication-ready figures.

``` python
import matplotlib.pyplot as plt
import pygmentation as pyg
from pygmentation.plot import apply_plot_styles, DocType

scheme = pyg.get_scheme("rose_pine", "light")

# Apply publication styles:
apply_plot_styles(scheme, doc_type=DocType.REPORT)

# Create figures as normal:
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 2], label="Series A")
ax.plot([1, 2, 3], [2, 4, 6], label="Series B")
ax.legend()
plt.show()
```

#### Document Types

The `DocType` enum controls layout geometry, typography, and contrast:

- **`DocType.REPORT`**: Tailored for articles, theses, and printed documents. Uses appropriate font sizes, a squarer aspect ratio, and carefully restricts colour to plot elements.
- **`DocType.PRESENTATION`**: Tailored for digital slides and presentations. Features enlarged typography, less cluttered axes, and more liberal use of colour to stand out.

![Sample graph produced with the Report styling.](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/sample_report.svg)

![Sample graph produced with the Presentation styling.](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/sample_report.svg)

#### System & LaTeX Font Discovery

The `get_fonts()` utility discovers and classifies installed system fonts, filtering by serif/sans-serif categories and LaTeX package compatibility:

``` python
from pygmentation.plot import get_fonts

# Discover all LaTeX-compatible serif fonts matching a pattern:
latex_serif_fonts = get_fonts(serif=True, latex=True, pattern="^Computer")

# `pattern` can take a list of patterns, and returns results in order. 
# This can be used to give a list of preferred fonts, and find the first available font:
preferred_font = get_fonts(pattern = ["Helvetica", "Calibri", "Arial", ".*"])[0]
```

A LaTeX installation is not a requirement for this module. If no LaTeX installation is found, any requests for LaTeX fonts will simply return an empty list, and LaTeX rendering will be disabled for matplotlib. The function `pygmentation.plot.is_latex_available()` can be used to check for a viable LaTeX installation. When LaTeX fonts are selected, `apply_plot_styles()` automatically injects the necessary `\usepackage{...}` declarations into Matplotlib's `text.latex.preamble`.

------------------------------------------------------------------------

## Command-Line Interface

The package includes a command-line interface for inspecting, previewing, and exporting palettes.

### `list`

Installed and user-registered colour schemes can be listed with the `list` command:

``` bash
# Filter with regex pattern:
pygmentation list "^nord"

# List all scheme names without swatches:
pygmentation list --names-only

# Preview swatches for all dark variants:
pygmentation list dark
```

![pygmentation list \".\*one.\*\"](https://raw.githubusercontent.com/ech0-chambers/pygmentation/refs/heads/refactor/.swatches/terminal_2.svg)

### `show`

A swatch table is rendered directly in the terminal using the `show` command:

``` bash
# Display light and dark variants of Nord:
pygmentation show nord

# Display only the dark variant:
pygmentation show nord dark

# Display swatches alongside specific colour model codes:
pygmentation show nord dark --code-type rgb
pygmentation show nord dark --code-type oklch
```

### `save`

A vector card can be exported directly to an SVG file:

``` bash
pygmentation save -f nord_dark.svg nord dark
```

When saving both variants (`both`), filenames are automatically suffixed with `_light.svg` and `_dark.svg`.

### `write`

The colour scheme can be exported into common formats using `write`:

``` bash
# Infer format from extension:
pygmentation write -f styles.css nord dark
pygmentation write -f colors.tex nord light

# Specify format explicitly:
pygmentation write -f palette.txt -t latex catppuccin dark
```

### Interactive Fuzzy Matcher

If a scheme name is mistyped, `pygmentation` queries the registry for schemes with similar names and prompts the user with possible suggestions:

    Unknown scheme 'norde'. Did you mean:
     1. nord (default)
     2. oriel
     3. novel
     4. None of the above (quit)
    Choose 1 to 4 (1): 

------------------------------------------------------------------------

## Output Formats Reference

### LaTeX (`xcolor`)

Definitions compatible with the `xcolor` package are emitted as standalone declarations. Foreground/background, accents, and surfaces are declared via `\definecolor`, while semantic aliases reference the originally defined colours via `\colorlet`:

``` latex
\definecolor{ForegroundColour}{HTML}{ECEFF4}
\definecolor{ForegroundColour_1}{HTML}{E1E5EA}
\definecolor{BackgroundColour}{HTML}{2E3440}
\definecolor{Accent1}{HTML}{5E81AC}
\definecolor{Accent1_1}{HTML}{A3B7D0}
\definecolor{Accent4}{HTML}{BF616A}
\definecolor{Accent4_1}{HTML}{DC9B9F}
% etc...

% Aliases reference canonical accent definitions:
\colorlet{Red}{Accent4}
\colorlet{Red_1}{Accent4_1}
\colorlet{Blue}{Accent1}
\colorlet{Error}{Accent4}
```

Colour identifiers are capitalised to avoid collisions with default LaTeX colour names (the built-in `red` and scheme colour `Red` exist simultaneously).

### CSS Custom Properties

CSS custom properties are wrapped in a `:root` block. For each colour, both a hexadecimal definition and an RGB component triplet (`-rgb`) are emitted:

``` css
:root {
  --clr-foreground: #ECEFF4;
  --clr-foreground-rgb: 236, 239, 244;
  --clr-foreground-1: #E1E5EA;
  --clr-foreground-1-rgb: 225, 229, 234;
  --clr-background: #2E3440;
  --clr-background-rgb: 46, 52, 64;
  --clr-accent1: #5E81AC;
  --clr-accent1-rgb: 94, 129, 172;
  --clr-accent4: #BF616A;
  --clr-accent4-rgb: 191, 97, 106;
  /* etc... */

  /* Aliases reference canonical variables: */
  --clr-red: var(--clr-accent4);
  --clr-red-rgb: var(--clr-accent4-rgb);
  --clr-red-1: var(--clr-accent4-1);
  --clr-red-1-rgb: var(--clr-accent4-1-rgb);
  --clr-error: var(--clr-accent4);
  --clr-error-rgb: var(--clr-accent4-rgb);
}
```

The companion `-rgb` variables allow opacity and alpha channels to be adjusted conveniently in stylesheets using `rgba(var(--clr-foreground-rgb), 0.5)` or `rgb(var(--clr-accent1-rgb) / 0.8)`.

### Less

Less variable declarations are generated using the `@clr-` prefix. Semantic aliases and status roles point directly to their target canonical variables:

``` less
@clr-foreground: #ECEFF4;
@clr-foreground-1: #E1E5EA;
@clr-background: #2E3440;
@clr-accent1: #5E81AC;
@clr-accent1-1: #A3B7D0;
@clr-accent4: #BF616A;
@clr-accent4-1: #DC9B9F;
// etc...

// Aliases reference canonical variables:
@clr-red: @clr-accent4;
@clr-red-1: @clr-accent4-1;
@clr-blue: @clr-accent1;
@clr-error: @clr-accent4;
```

### Textual CSS (`.tcss`)

Variables for [Textual terminal applications](https://github.com/textualize/textual) are emitted with the `$clr-` prefix, following Textual's styling conventions:

``` less
$clr-foreground: #ECEFF4;
$clr-foreground-1: #E1E5EA;
$clr-background: #2E3440;
$clr-accent1: #5E81AC;
$clr-accent1-1: #A3B7D0;
$clr-accent4: #BF616A;
$clr-accent4-1: #DC9B9F;
// etc...

// Aliases reference canonical variables:
$clr-red: $clr-accent4;
$clr-red-1: $clr-accent4-1;
$clr-blue: $clr-accent1;
$clr-error: $clr-accent4;
```

### JavaScript

A structured JavaScript object is generated containing nested families for the foreground, background, accents, surfaces, and auto-generated surface. Aliases are assigned as direct object references to the canonical accent families:

``` javascript
const colors = {
  foreground: {
    base: "#ECEFF4",
    0: "#ECEFF4",
    1: "#E1E5EA",
    variants: [ "#E1E5EA", "#D7DAE0", ... ],
  },
  background: {
    base: "#2E3440",
    0: "#2E3440",
    1: "#878C95",
    variants: [ "#878C95", "#585E69", ... ],
  },
  accents: [
    { base: "#5E81AC", 0: "#5E81AC", variants: [ ... ] },
    // etc...
  ],
  surfaces: [
    // ...
  ],
  auto_surface: { base: "#232833", ... },
};

// Aliases reference canonical accent objects:
colors.red = colors.accents[3];
colors.blue = colors.accents[0];
colors.error = colors.accents[3];
```

### SVG Swatch Cards

Swatch cards (such as those used in this README) are written as SVG files. Swatch layout dimensions and aspect ratios can be configured programmatically via `SvgExporter`, and the colour codes can be included as well:

``` python
from pygmentation.exporters import SvgExporter

exporter = SvgExporter(
    base_aspect_ratio=2.0,
    variant_aspect_ratio=1.0,
    swatch_height=33,
    code_type = "hsl"
)
svg_content = exporter.export(scheme)
```

------------------------------------------------------------------------

## Custom Schemes & Extensibility

You can register custom colour schemes in two ways:

### 1. User Configuration File

`pygmentation` automatically checks for user-defined schemes in `~/.config/pygmentation/color_schemes.json`. Schemes placed here are discovered alongside built-in themes:

``` json
{
  "my_custom_theme": {
    "foreground": "#F8F8F2",
    "background": "#282A36",
    "accents": [
      "#FF79C6",
      "#BD93F9",
      "#50FA7B",
      "#FFB86C"
    ]
  }
}
```

These schemes must define a `foreground` and `background` colour, and an `accents` list.

### 2. Programmatic Registration

Register or unregister schemes dynamically at runtime (registered schemes are *not* saved to the custom schemes file):

``` python
from pygmentation import registry

registry.register("my_theme", {
    "foreground": "#FFFFFF",
    "background": "#111111",
    "accents": ["#FF0055", "#00FFAA"]
})

scheme = registry.get("my_theme", "dark")
```

------------------------------------------------------------------------

## Development & Quality Gates

The `pygmentation` test suite and linters enforce strict typing and code style:

``` bash
# Run full unit test suite:
pytest

# Check linting and code formatting:
ruff check src tests

# Static type checking:
mypy src
```
