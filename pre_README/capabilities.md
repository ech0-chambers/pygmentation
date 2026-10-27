- Sophisticated handling of colours, colour models/spaces and their conversions, and colour manipulations
- Context-aware generation of tints and shades, ensuring colour variants are harmonious with the foreground/background colours
- Full palette generation from a handful of base colours -- only a foreground, background, and one or more accent colours are needed
- Highly consistent naming and structure across schemes -- specifying colours by their position in the scheme (e.g. `Accent 1`) allows projects to easily take on the "vibe" of a particular palette, while semantic aliases like `Blue` or `Error` allow deliberate use of colours to communicate meaning
- Consistent contrast across light and dark themes -- a colour variant with good contrast to the background will maintain that contrast regardless of the scheme, in both light and dark themes
- Exporters for common formats, including LaTeX, CSS, JavaScript, and less.js, with an easily extensible base class for custom exporters
- Direct integration with Matplotlib to apply consistent styling across plots, with significant font handling capabilities

### Scheme Overview

All schemes must have at least a foreground colour, a background colour, and at least one (usually six or more) accent colour. Some may also define any number of surface colours, though these are optional. In a light scheme, the background colour must be lighter than the foreground, and vice versa for a dark scheme. 

Each colour in the scheme receives 5 variants, which are lighter/darker variants generated in a way that keeps them harmonious with the rest of the colour scheme. For details on this generation, see [Variant Derivation](#variant-derivation). Together with the base colour, these are known collectively as a colour family. A colour family's variants are ordered by their contrast to the background colour, from most contrast to least contrast. Usually, the base colour will sit between variant 2 and variant 3, though this is not always the case. As an example, the dark theme for the [Nord colour scheme](https://www.nordtheme.com/) is shown below, with its variant colours.

%%md.image(url = ("" if USE_RELATIVE else URL_BASE) + str(IMAGE_DIR / "nord.svg"), description = "The Nord dark colour scheme rendered by Pygmentation.")
