To appreciate how `pygmentation` derives its colour families, it is helpful to examine the colour science that underpins the package.

### Why Geometric Colour Spaces Fail Human Vision

Human vision does not perceive light linearly; the human eye is far more sensitive to green wavelengths than to deep blue or deep red. Because the RGB and HSL models are coordinate representations based on display hardware, all colour channels are treated symmetrically. 

Furthermore, geometric models do not account for the Helmholtz-Kohlrausch effect, in which vivid, highly saturated colours are perceived as brighter than muted colours of identical physical luminance -- a saturated yellow light is perceived as brighter than a white light.

When "lightness" is altered in HSL, a linear calculation is performed on a non-linear perceptual space. This results in visual inconsistency: adjusting two different colours by the same "20% lightness" produces two noticeably different changes in perceived brightness.

For example, we may start from a pure blue and a pure yellow, and lighten both by 20% in HSL. For blue, this produces a noticeable change: %%comparison_swatch(HSL(240, 1, 0.5), HSL(240, 1, 0.7)). For yellow, however, the difference is nearly negligible, if anything appearing slightly washed out instead of lightened: %%comparison_swatch(HSL(60, 1, 0.5), HSL(60, 1, 0.7)). In darker tones, the difference is reversed with yellow showing a larger change than blue when darkened by 20%: %%comparison_swatch(HSL(240, 1, 0.5), HSL(240, 1, 0.3)) compared to %%comparison_swatch(HSL(60, 1, 0.5), HSL(60, 1, 0.3)).

### Perceptual Uniformity: CIEDE2000 and Oklab / Oklch

A perceptually uniform colour model is one in which a given change in coordinates produces the same visual change, regardless of the starting position. To put things more mathematically, if a starting colour $\vec{C}$ is shifted by some $\vec{t}$ to give a new colour $\vec{C^\prime} = \vec{C} + \vec{t}$, then the visual difference between $\vec{C}$ and $\vec{C^\prime}$ is always the same, no matter what $\vec{C}$ was.

Neither RGB nor HSL are perceptually uniform. In terms of lightness, this is made clear by the comparison of yellow and blue above. For hue, this is readily demonstrated by comparing the perceived difference between two green hues and two blue hues separated by an identical $30^\circ$ angle in HSL:

- Green at $100^\circ$ and $130^\circ$: %%comparison_swatch(HSL(100, 1, 0.5), HSL(130, 1, 0.5)).
- Blue at $260^\circ$ and $290^\circ$: %%comparison_swatch(HSL(260, 1, 0.5), HSL(290, 1, 0.5)).

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

In 2020, Björn Ottosson published Oklab, a perceptual colour space designed using experimental data on human colour perception (see [https://bottosson.github.io/posts/oklab/](https://bottosson.github.io/posts/oklab/)). Like CIELab, Oklab represents colours as a lightness, $a$ (red-green dimension), and $b$ (blue-yellow dimension). It is much closer to being perceptually uniform, so much so that the Euclidean distance between colours is sufficient to replace the computationally expensive CIEDE2000 calculation.

When transformed into polar coordinates, this space is referred to as Oklch:

- $L$: Perceptual lightness.
- $C = \sqrt{a^2 + b^2}$: Perceptual chroma (a concept similar to saturation).
- $h = \text{atan2}(b, a)$: Hue angle in degrees ($0^\circ \le h < 360^\circ$).

Oklab eliminates the hue-shifting issues seen in CIELAB and HSL: altering lightness in Oklab does not cause blue hues to drift into purple. Within `pygmentation`, Oklab and Oklch are used for the canonical "true" values of colours. All colour manipulations happen in Oklab and Oklch space, and colours are stored and compared by their Oklab values, converting to other colour models for output or model-specific manipulations.

---

### Consistent Contrast

Colour schemes in `pygmentation` are intended to be as close to drop-in replacements for each other as possible, regardless of the number of colours, colour order, and light/dark theming. This makes it vitally important that colours which have good contrast in one theme also have good contrast in another. Of course, this is very hard to enforce between accent colours without imposing restrictions on the colour schemes. However, we can ensure that contrast against the background and foreground colours is consistent. Within each colour family, the variants are always ordered from most contrast with the background colour to least contrast with the background colour. Compare the images below for the Nord dark scheme and the Rose Pine Dawn light scheme.

%%md.image(url = ("" if USE_RELATIVE else URL_BASE) + str(IMAGE_DIR / "nord.svg"), description = "The Nord dark colour scheme rendered by Pygmentation.")

%%md.image(url = ("" if USE_RELATIVE else URL_BASE) + str(IMAGE_DIR / "rose_pine_dawn.svg"), description = "The Rose Pine Dawn light colour scheme rendered by Pygmentation.")


---

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

$$C_{\text{variant}} = C_{\text{base}} + (C_{\text{F or B}} - C_{\text{base}}) \times x \times \text{chroma\_blend}$$

By default, $\text{chroma\_blend} = 0.75$. This subtle shift prevents saturated accents from appearing unnatural on desaturated background, without appearing washed out if the background colour has high saturation. The sample below has this chroma blend disabled; the darker variants in particular stand out and are quite jarring.

%%md.image(url = ("" if USE_RELATIVE else URL_BASE) + str(IMAGE_DIR / "nord_no_chroma.svg"), description = "The Nord dark colour scheme with chroma blending disabled for variants.")

#### Ambient Hue Alignment

When a base colour's hue is already very close to the background or foreground anchor (within $30^\circ$ in Oklch), it can produce better results to subtly shift the hue as well. In this case, instead of lightening/darkening and adjusting the chroma, the variant is simply a linear interpolation between the original colour and the foreground or background colour, evaluated in Oklab space. Because the foreground and background are considered separately, it is possible (and likely) that a colour's lighter variants are directly lightened, while its darker variants are interpolated towards the foreground/background colour, or vice versa. Taking the Nord scheme as an example again, in the dark theme accent colours 1 and 3 exhibit this behaviour, linearly interpolating towards the background colour.
