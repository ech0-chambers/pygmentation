# API Reference

Pygmentation organizes its API across several focused modules:

| Submodule                 | Topic                  | Description                                                                           |
| ---                       | ---                    | ---                                                                                   |
| `pygmentation.colors`     | Colour Handling        | Perceptual colour representation, colour models, and structured palettes.             |
| `pygmentation.plot`       | Matplotlib Plotting    | Publication styling (`apply_plot_styles`), document presets, and font utilities.      |
| `pygmentation.exporters`  | Exporters              | Exporters for CSS, Less, Textual CSS, LaTeX (`xcolor`), JavaScript, and SVG swatches. |
| `pygmentation.registry`   | Registry               | The global scheme registry for built-in and user-configured palettes.                 |
| `pygmentation.cli`        | Command-Line Interface | CLI commands for inspecting, previewing, and exporting schemes.                       |
| `pygmentation.exceptions` | Exceptions             | Custom exception hierarchy for Pygmentation.                                          |

## Top-Level Functions

Most of the common functions and classes are available from the top-level module. These include:

- `Color`: The main class for handling individual colours.
- `ColorFamily`: For handling families containing a base colour and its variants.
- `ColorScheme`: For generating and interacting with a full colour scheme.
- `registry`: An initialised instance of `SchemeRegistry`.
- [`get_scheme()`](registry.md#pygmentation.registry.SchemeRegistry.get): An alias for `registry.get()`, for loading a colour scheme.
- [`list_schemes()`](registry.md): An alias for `registry.available`, returns the full list of available schemes, including the built-in schemes and any custom user-defined schemes.
- [`register_scheme()`](registry.md#pygmentation.registry.SchemeRegistry.register): An alias for `registry.register()`, for adding a new scheme to the registry.
- [`unregister_scheme()`](registry.md#pygmentation.registry.SchemeRegistry.unregister): An alias for `registry.unregister()`, for removing a scheme from the registry.
- `has_scheme()`: An alias for `registry.has_scheme()`, for checking the availability of a scheme in the registry.
- `get_exporter()`: For getting an `Exporter` instance for a given output format.

