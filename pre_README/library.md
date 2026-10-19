The top-level namespace provides access to all core classes, functions, and the scheme registry:

```python
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

```python
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

* **Standard Families:**
  - `scheme.foreground`: The foreground colour family.
  - `scheme.background`: The background colour family.
  - `scheme.accents`: A list of all accent colour families (`list[ColorFamily]`).
  - `scheme.surfaces`: A list of explicitly defined surface colour families (may be empty).
  - `scheme.auto_surface`: An automatically synthesised surface colour family balancing contrast and background tint.

* **Semantic Aliases:**
  - `scheme.red`, `scheme.orange`, `scheme.yellow`, `scheme.green`, `scheme.cyan`, `scheme.blue`, `scheme.purple`, `scheme.magenta`.
  - Functional roles: `scheme.error`, `scheme.warning`, `scheme.success`, `scheme.info`.

* **Distinct Accents:**
  - `scheme.distinct`: Returns a list of accent colour families with similar colours filtered out. This is in the same order as `scheme.accents`.
  - `scheme.high_contrast(n)`: Fetch the `n` accent colours which collectively are as different as possible. 

* **Iteration:**
  - Iterating over a scheme yields all colour families (foreground, background, accents, surfaces, and auto-surface).

### The `ColorFamily` Object

A `ColorFamily` encapsulates a base colour and its five derived variants:

* **Variant Access:**
  - `family.base`: The underlying base `Color` object.
  - `family[0]`: Equivalent to `family.base`.
  - `family[1]` through `family[5]`: The five contrast-ordered variant `Color` objects.
  - `ColorFamily` instances are iterable and can be used in list unpacking. `base, *variants = family` will work as expected.
  - `family.lightest`: Returns the variant with the highest Oklab lightness.
  - `family.darkest`: Returns the variant with the lowest Oklab lightness.

### The Immutable `Color` Value Object

The `Color` class represents a single colour. It is implemented as a frozen, immutable value object; methods never modify the existing instance in place, but instead return a new `Color`. Therefore, it is hashable and safe to use for dictionary keys.

```python
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

```python
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

```python
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

---

### Matplotlib Publication Styling

With the `[plots]` extra installed, `pygmentation.plot` configures Matplotlib's `rcParams` to match your chosen colour scheme for publication-ready figures.

```python
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

%%md.image(url = ("" if USE_RELATIVE else URL_BASE) + str(IMAGE_DIR / "sample_report.svg"), description = "Sample graph produced with the Report styling.")

%%md.image(url = ("" if USE_RELATIVE else URL_BASE) + str(IMAGE_DIR / "sample_report.svg"), description = "Sample graph produced with the Presentation styling.")

#### System & LaTeX Font Discovery

The `get_fonts()` utility discovers and classifies installed system fonts, filtering by serif/sans-serif categories and LaTeX package compatibility:

```python
from pygmentation.plot import get_fonts

# Discover all LaTeX-compatible serif fonts matching a pattern:
latex_serif_fonts = get_fonts(serif=True, latex=True, pattern="^Computer")

# `pattern` can take a list of patterns, and returns results in order. 
# This can be used to give a list of preferred fonts, and find the first available font:
preferred_font = get_fonts(pattern = ["Helvetica", "Calibri", "Arial", ".*"])[0]
```

A LaTeX installation is not a requirement for this module. If no LaTeX installation is found, any requests for LaTeX fonts will simply return an empty list, and LaTeX rendering will be disabled for matplotlib. The function `pygmentation.plot.is_latex_available()` can be used to check for a viable LaTeX installation. When LaTeX fonts are selected, `apply_plot_styles()` automatically injects the necessary `\usepackage{...}` declarations into Matplotlib's `text.latex.preamble`.
