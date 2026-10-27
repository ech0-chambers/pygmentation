# Scheme Palettes

Search and explore the built-in colour schemes available in `pygmentation`. The palettes shown here are the result of running 

```bash
python3 -m pygmentation save <scheme_name> <light|dark> -f filename.svg
```

Hover each swatch to see its hex sRGB representation, and click to copy.

<div class="pyg-palette-explorer">
  <div class="pyg-palette-controls">
    <div class="pyg-palette-control-group pyg-search-group">
      <label for="pyg-palette-search" class="pyg-label">Search:</label>
      <input type="text" id="pyg-palette-search" class="md-input pyg-search-input" placeholder="Search schemes (e.g. nord, catppuccin, gruvbox)..." autocomplete="off" />
    </div>

    <div class="pyg-palette-control-group pyg-select-group">
      <label for="pyg-palette-select" class="pyg-label">Scheme:</label>
      <select id="pyg-palette-select" class="md-input pyg-select">
        <!-- Populated dynamically -->
      </select>
    </div>

    <div class="pyg-palette-control-group pyg-toggle-group-wrapper">
      <label class="pyg-label">Variant:</label>
      <div class="pyg-toggle-group">
        <button type="button" class="md-button pyg-palette-toggle" data-variant="light">Light</button>
        <button type="button" class="md-button md-button--primary pyg-palette-toggle active" data-variant="dark">Dark</button>
      </div>
    </div>
  </div>

  <div id="pyg-palette-display" class="pyg-palette-display"></div>
  <div id="pyg-swatch-tooltip" class="pyg-swatch-tooltip" style="display: none;"></div>
</div>
