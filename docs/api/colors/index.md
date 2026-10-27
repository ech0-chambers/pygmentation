# Colour Handling

The `pygmentation.colors` submodule provides access to the underlying classes and algorithms for handling and manipulating colours, conversions between colour models, and managing a full colour scheme.

## Submodule Overview
Pygmentation's colour architecture is built in three layers:

1. **Low-Level Colour Models (`pygmentation.colors.models`):** Implementations of several colour models, including geometric models like sRGB and HSL, and perceptual models including CIE XYZ, CIE LAB, and Oklab. Conversions are also handled here.
2. **Core Colour Representation (`pygmentation.colors.color`):** The immutable `Color` class, which maintains colours in Oklab space and provides perceptual manipulation methods (`lighten`, `darken`, `lerp`, CIEDE2000 distance).
3. **Structured Palettes (`pygmentation.colors.scheme`):** The `ColorFamily` class holds information relating to a single colour and its variants within the context of a scheme, while the `ColourScheme` class holds a collection of `ColorFamily` objects which together form a coherent scheme. 

### Scheme Overview

All schemes must have at least a foreground colour, a background colour, and at least one (usually six or more) accent colour. Some may also define any number of surface colours, though these are optional. In a light scheme, the background colour must be lighter than the foreground, and vice versa for a dark scheme. 

Each colour in the scheme receives 5 variants, which are lighter/darker variants generated in a way that keeps them harmonious with the rest of the colour scheme. Together with the base colour, these are known collectively as a colour family. A colour family's variants are ordered by their contrast to the background colour, from most contrast to least contrast. Usually, the base colour will sit between variant 2 and variant 3, though this is not always the case. 

### Variant Generation

Variants are calculated by scaling lightness in Oklab space. In standard cases, variants are generated using fractional adjustments:

- In a **light scheme**, variants are 50% and 25% darker, and 40%, 60%, and 80% lighter.
- In a **dark scheme**, the directions are inverted: variants are 50% and 25% lighter, and 40%, 60%, and 80% darker.

Here, "20% lighter" doesn't mean that the lightness is increased by 20%. Instead, it means that the lightness is increased to be 20% closer to full lightness. In other words, a colour with lightness $l$ which is lightened by some amount $p < 1$ has final lightness $l^\prime = l + (1 - l) \times p$. For darkening by an amount $p < 1$, $l^\prime = l \times (1 - p)$. In fact, in `pygmentation` schemes, the maximum and minimum lightness is usually that of the background/foreground colours instead of 1 and 0, keeping variants context-aware so that they can never become lighter/darker than the foreground/background colours.

There are exceptions and adjustments to these general rules, outlined below.

#### Contrast Bounds Clamping

To prevent lighter variants from washing out into a light background, and darker variants from collapsing into a dark background, the target lightness is clamped. For darkening, the target lightness cannot be below 0.2, and for lightening it cannot be above 0.8.

#### Extreme Base Colours and Array Inversion

If a base colour has an extreme lightness, generating variants in the same way is significantly less useful. A very light base colour in a dark theme would result in the base colour and three lighter variants being almost indistinguishable, while the two darker variants represent huge visual jumps. Determining whether a colour is "too light" or "too dark" is done by considering how extreme its lightness is compared to the foreground/background lightness. If $l_B$ and $l_F$ are the lightnesses of the background and foreground colours respectively (clamped as described above), then a colour with lightness $l$ is considered too light if $\frac{l - 0.5}{\max(l_F, l_B) - 0.5} > 0.8$, and too dark if $\frac{0.5 - l}{0.5 - \min(l_F, l_B)} > 0.8$. In other words, we ask "Compared to a pure mid-tone, is the colour at least 80% as light as the foreground/background colour? Compared to a pure mid-tone, is it at least 80% as dark as the foreground/background colour?", choosing between foreground and background based on whether we are considering a light or dark theme.

For base colours deemed too dark or too light for the normal variant generation, variants are produced which are 10%, 25%, 50%, 75%, and 90% lighter or darker. The order of these variants is reversed in a dark theme, to maintain the usual order of contrast with the background colour.

#### Fractional Chroma Blending

Changing only the lightness produces subpar results, with dark variants looking particularly out of place and oversaturated. To keep variants more harmonious with the foreground/background colours, the chroma of the base colour is also modified. A variant's chroma is shifted towards the chroma of the foreground/background colour by the same amount by which it is lightened/darkened, multiplied by an additional factor `chroma_blend`.

$$C_{\text{variant}} = C_{\text{base}} + (C_{\text{F or B}} - C_{\text{base}}) \times x \times C_{\text{blend}}$$

By default, `chroma_blend = 0.75`. This subtle shift prevents saturated accents from appearing unnatural on desaturated background, without appearing washed out if the background colour has high saturation.

#### Ambient Hue Alignment

When a base colour's hue is already very close to the background or foreground anchor (within $30^\circ$ in Oklch), it can produce better results to subtly shift the hue as well. In this case, instead of lightening/darkening and adjusting the chroma, the variant is simply a linear interpolation between the original colour and the foreground or background colour, evaluated in Oklab space. Because the foreground and background are considered separately, it is possible (and likely) that a colour's lighter variants are directly lightened, while its darker variants are interpolated towards the foreground/background colour, or vice versa. Taking the Nord scheme as an example again, in the dark theme accent colours 1 and 3 exhibit this behaviour, linearly interpolating towards the background colour.
