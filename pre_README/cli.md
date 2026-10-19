The package includes a command-line interface for inspecting, previewing, and exporting palettes.

### `list`

Installed and user-registered colour schemes can be listed with the `list` command:

```bash
# Filter with regex pattern:
pygmentation list "^nord"

# List all scheme names without swatches:
pygmentation list --names-only

# Preview swatches for all dark variants:
pygmentation list dark
```

%%capture_terminal("pygmentation list \".*one.*\"")

### `show`

A swatch table is rendered directly in the terminal using the `show` command:

```bash
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

```bash
pygmentation save -f nord_dark.svg nord dark
```

When saving both variants (`both`), filenames are automatically suffixed with `_light.svg` and `_dark.svg`.

### `write`

The colour scheme can be exported into common formats using `write`:

```bash
# Infer format from extension:
pygmentation write -f styles.css nord dark
pygmentation write -f colors.tex nord light

# Specify format explicitly:
pygmentation write -f palette.txt -t latex catppuccin dark
```

### Interactive Fuzzy Matcher

If a scheme name is mistyped, `pygmentation` queries the registry for schemes with similar names and prompts the user with possible suggestions:

```
Unknown scheme 'norde'. Did you mean:
 1. nord (default)
 2. oriel
 3. novel
 4. None of the above (quit)
Choose 1 to 4 (1): 
```
