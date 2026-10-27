### LaTeX (`xcolor`)

Definitions compatible with the `xcolor` package are emitted as standalone declarations. Foreground/background, accents, and surfaces are declared via `\definecolor`, while semantic aliases reference the originally defined colours via `\colorlet`:

```latex
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

```css
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

```less
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

```less
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

```javascript
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

```python
from pygmentation.exporters import SvgExporter

exporter = SvgExporter(
    base_aspect_ratio=2.0,
    variant_aspect_ratio=1.0,
    swatch_height=33,
    code_type = "hsl"
)
svg_content = exporter.export(scheme)
```
