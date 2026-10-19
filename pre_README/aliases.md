While colours can always be accessed by their position in the scheme (e.g, `var(--clr-accent1)` in the CSS output), semantic aliases (red, orange etc) are automatically identified by matching accent colours to canonical hue targets in Oklch space. Matches are determined globally, which allows a small adjustment to discourage multiple aliases mapping to the same colour. The target hues and acceptable ranges are defined as follows:

%%md.image(url = ("" if USE_RELATIVE else URL_BASE) + str(IMAGE_DIR / "reference_colors.svg"), description = "OKLCh reference hue ranges and target angles for semantic colour aliases")

In addition, four functional aliases are mapped:

- **`error`**: maps to `red`
- **`warning`**: maps to `yellow` (or sometimes `orange`, if `yellow` is the same as `green` which can happen in some schemes)
- **`success`**: maps to `green`
- **`info`**: maps to `blue`

Every alias is resolved to the nearest accent colour using Oklch hue proximity and Oklab distance. It is possible for multiple aliases to map to the same colour, for example in the Nord scheme `magenta` and `purple` both map to the same colour.
