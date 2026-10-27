# Matplotlib Plotting

The `pygmentation.plot` submodule provides easy integration of `pygmentation` colour schemes into Matplotlib plots, as well as some helpful default stylings for reports and presentations, and font discovery functions.

## Submodule Overview

The plotting integration is divided into three functional domains:

1. **Styling & Presets (`pygmentation.plot.style`):** The `apply_plot_styles` function sets Matplotlib rcParams for specific intended uses (e.g. `DocType.REPORT` for articles, documents etc; or `DocType.PRESENTATION` for presentations and posters), creates a colour cycler to use a `pygmentation` scheme's accent colours for plot elements, enables/disables LaTeX text rendering, and sets fonts (including adding the necessary packages to the LaTeX preamble). 
2. **Font Discovery (`pygmentation.plot.fonts`):** Searches system fonts and TeX-live/MikTeX fonts (`get_fonts`, `is_latex_available`) to identify available fonts and (for LaTeX fonts) any necessary packages, searching by name and serif/sans-serif attributes.
3. **Font Classification (`pygmentation.plot.font_category`):** Categorises available fonts as serif or sans-serif (`FontCategory`, `classify_font_name`).

