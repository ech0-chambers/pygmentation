
### Python Library

```python
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

```bash
pygmentation write nord dark -f nord.css
```

Display any colour scheme in your terminal with rich full-colour swatches:

```bash
pygmentation show nord dark
```

%%capture_terminal("pygmentation show nord dark", columns = 112)
