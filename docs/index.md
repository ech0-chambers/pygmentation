# Pygmentation

A colour manipulation and palette generation package with optional Matplotlib integration.

## Key Features

- Sophisticated handling of colours, colour models/spaces and their conversions, and colour manipulations
- Context-aware generation of tints and shades, ensuring colour variants are harmonious with the foreground/background colours
- Full palette generation from a handful of base colours -- only a foreground, background, and one or more accent colours are needed
- Highly consistent naming and structure across schemes -- specifying colours by their position in the scheme (e.g. `Accent 1`) allows projects to easily take on the "vibe" of a particular palette, while semantic aliases like `Blue` or `Error` allow deliberate use of colours to communicate meaning
- Consistent contrast across light and dark themes -- a colour variant with good contrast to the background will maintain that contrast regardless of the scheme, in both light and dark themes
- Exporters for common formats, including LaTeX, CSS, JavaScript, and less.js, with an easily extensible base class for custom exporters
- Direct integration with Matplotlib to apply consistent styling across plots, with significant font handling capabilities

## Installation

Install the core package:

```bash
pip install pygmentation
```

To include Matplotlib styling and font utilities:

```bash
pip install "pygmentation[plots]"
```

For documentation dependencies:

```bash
pip install "pygmentation[docs]"
```

## Quickstart

```python
import pygmentation as pyg

# Load a colour scheme (light or dark)
scheme = pyg.get_scheme("nord", "dark")

# Access base colours and semantic aliases
bg_color = scheme.background.base.hex         # "2E3440"
red_base = scheme.red.base.css                # "#BF616A"

# Access derived variants (variant 1 has highest contrast to background)
red_high_contrast = scheme.red[1].css         # "#DC9B9F"

# Convert seamlessly to other colour models
r, g, b = scheme.red.base.rgb.as_255          # (191, 97, 106)
l, a, b = scheme.red.base.oklab

# Optional Matplotlib integration
from pygmentation.plot import apply_plot_styles

# apply default styling and colour scheme to matplotlib plots
apply_plot_styles("nord", "light")
```

## Command-Line Usage

Several functions are available from the command line. 


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

When saving both variants (`both`), filenames are automatically suffixed with `_light.svg` and `_dark.svg`. Examples of these cards can be seen in [Palettes](palettes.md).

### `write`

The colour scheme can be exported into common formats using `write`:

```bash
# Infer format from extension:
pygmentation write -f styles.css nord dark
pygmentation write -f colors.tex nord light

# Specify format explicitly:
pygmentation write -f palette.txt -t latex catppuccin dark
```


## Examples

Below are some realistic samples using schemes available in `pygmentation`. A small handful of schemes can be selected, and toggled between the light and dark theme. 

<div class="pyg-example-card" data-scheme="nord" data-variant="dark">
  <!-- Header Controls -->
  <div class="pyg-card-header">
    <div class="pyg-scheme-controls">
      <div class="pyg-scheme-selector-container">
      <label for="pyg-scheme-select" class="pyg-label">Scheme:</label>
      <select id="pyg-scheme-select" class="md-input pyg-select">
        <option value="nord" selected>Nord</option>
        <option value="rose_pine">Rosé Pine</option>
        <option value="catppuccin">Catppuccin</option>
        <option value="twilight">Twilight</option>
        <option value="japanesque">Japanesque</option>
      </select>
      </div>
      <div class="pyg-toggle-group">
        <button type="button" class="md-button pyg-button-toggle" data-variant="light">Light</button>
        <button type="button" class="md-button md-button--primary pyg-button-toggle active" data-variant="dark">Dark</button>
      </div>
    </div>
    <div class="pyg-tab-nav">
      <button type="button" class="pyg-tab-button active" data-tab="webpage">Article</button>
      <button type="button" class="pyg-tab-button" data-tab="code">Code</button>
      <button type="button" class="pyg-tab-button" data-tab="graph">Graph</button>
    </div>
  </div>

  <!-- Content Area -->
  <div class="pyg-preview" data-scheme="nord" data-variant="dark">
    
    <!-- Tab 1: Article Example (Scrollable scientific paper excerpt) -->
    <div id="pyg-tab-webpage" class="pyg-tab-pane" style="display: block;">
      <article class="pyg-demo-article">
        <!-- Article Header -->
        <header class="pyg-article-header">
          <div class="pyg-article-meta">
            <span class="pyg-badge">Aspernatur Ipsam, Mar. 1860</span>
            <span class="pyg-badge">Asperiores: Dignissimos</span>
            <span class="pyg-badge">Asperiores: Reprehenderit Beatae</span>
            <span class="pyg-badge">Eveniet: Voluptas Saepe</span>
          </div>
          <h2 class="pyg-article-title">Magni Perspiciatis et Quisquam Facilis</h2>
          <p class="pyg-article-subtitle">Et Consequuntur ad Laborum Voluptate Temporibus</p>
          <p class="pyg-article-byline">Prof. L. Ipsum et al.</p>
          <div class="pyg-article-actions">
            <button type="button" class="pyg-demo-button pyg-button-primary" id="pyg-cite-button">Cite Article</button>
            <button type="button" class="pyg-demo-button pyg-button-secondary" id="pyg-copy-ref-button">Copy Reference</button>
          </div>
        </header>

        <!-- Section 1 -->
        <section class="pyg-article-section">
          <h3 class="pyg-section-heading">&sect; I. Accusamus Rem</h3>
          <p>
            Accusamus culpa ex commodi praesentium, ad expedita sunt eveniet ut ullam beatae provident minus officiis velit, a hic cupiditate, harum dolorum commodi quos nostrum quae sed alias nam? Quo illo quod vel repellat dignissimos corporis nisi consequatur architecto sint ratione, ullam atque veniam illum corporis.
          </p>
          <p>
            Laborum ex voluptatum voluptate iusto, qui et id culpa quasi nostrum distinctio consectetur fugit facilis, autem delectus voluptates. Porro accusamus temporibus molestiae provident, vero labore illo ut provident nostrum mollitia et cupiditate necessitatibus cumque. Porro deleniti veniam architecto est dignissimos ut adipisci?
          </p>
          <aside class="pyg-demo-aside">
            <strong>Illo Sequi hic Dolores</strong>
            Sed commodi necessitatibus possimus culpa iure accusamus perferendis dolor expedita repellat laborum, cumque alias necessitatibus inventore praesentium quod nostrum facilis porro incidunt. Veritatis ut cum veniam, minima dolor officia quod impedit blanditiis voluptate velit suscipit numquam nemo.
          </aside>
        </section>

        <!-- Section 2 -->
        <section class="pyg-article-section">
          <h3 class="pyg-section-heading">&sect; II. Suscipit Quae Minus Tempora</h3>
--8<-- "docs/snippets/diagram.svg"
          <p>
            Quaerat ipsum vitae aut officia voluptatum quas dolorum assumenda blanditiis doloremque, porro voluptas laudantium provident delectus saepe ipsum accusamus reiciendis optio, sed id molestias dicta dolorem magni tenetur. Quae molestiae corrupti iusto recusandae aut minima dolor magni quaerat possimus quos, aspernatur ex expedita delectus repellendus? Voluptatum debitis eligendi soluta pariatur non autem aliquid ea.
          </p>
          <p>
            Repudiandae voluptatem aut animi, incidunt culpa quibusdam laudantium vitae facilis cumque quasi ducimus explicabo maiores obcaecati. Praesentium aliquid rem, sequi atque vel nihil quibusdam dolorem quae sunt, illo corporis ducimus sit ipsam laborum fugit, assumenda hic architecto reiciendis excepturi quo tempora fuga eveniet velit culpa. Nihil sint cum impedit recusandae nulla asperiores distinctio nemo?
          </p>
          <aside class="pyg-demo-aside">
            <strong>Ex Temporibus Deleniti Necessitatibus</strong>
            Quam nam voluptates doloribus dolore, unde sapiente delectus, quam quasi vitae perspiciatis nam delectus incidunt culpa itaque? Quibusdam rem culpa possimus qui repellat quam magnam sit, voluptates ipsum quis sit amet sequi aut officiis natus. Perspiciatis vitae obcaecati nesciunt laudantium commodi reprehenderit maxime itaque ad, saepe corporis rerum fugiat, enim nesciunt consequuntur modi.
          </aside>
        </section>

        <!-- Section 3 -->
        <section class="pyg-article-section">
          <h3 class="pyg-section-heading">&sect; III. Aperiam Distinctio Iure Modi</h3>
          <p>
            Vel minima enim, atque incidunt facere ex dignissimos quam voluptates saepe aliquam veniam illum corporis, recusandae a mollitia beatae enim voluptate obcaecati, quo nulla repellat repellendus perferendis cumque? Mollitia saepe minus repellat excepturi ducimus, ipsam voluptatibus vel quam sapiente, perspiciatis pariatur corrupti error illum est blanditiis. Odio animi enim, repellat minima veritatis cupiditate?
          </p>
          <p>
            Officia fugiat alias modi quis, ex necessitatibus dicta molestias nobis, repudiandae rem sapiente fugiat vel voluptas. Rerum iure laboriosam facilis tempore, quasi quibusdam id repudiandae at rerum iure. Unde nobis corrupti sapiente aliquam obcaecati quod magni non quibusdam? Veniam voluptates facilis aperiam doloribus error, ut asperiores in iusto enim maiores molestiae consequatur, doloribus deserunt accusamus animi consequuntur ratione ipsa cum qui at?
          </p>
          <aside class="pyg-demo-aside">
            <strong>Dolores Eveniet Laborum Sapiente</strong>
            Expedita voluptate voluptates perferendis nulla laboriosam minima nobis cum, at qui ratione labore ut laboriosam? Temporibus qui id consequatur totam, voluptas cumque distinctio vero labore inventore sint ducimus quis dolores molestias debitis, ex natus doloremque quam iusto necessitatibus officiis amet repellendus. Sit vero modi tenetur officiis accusantium praesentium, sunt dolorem sequi iste, praesentium voluptate quae accusantium nam.
          </aside>
        </section>
      </article>
    </div>

    <!-- Tab 2: Code Sample Example -->
    <div id="pyg-tab-code" class="pyg-tab-pane" style="display: none;">
      <pre class="pyg-code-block"><code><span class="kw">def</span> <span class="fn">darker</span><span class="punct">(</span><span class="param">self</span><span class="punct">,</span> <span class="param">amount</span><span class="punct">:</span> <span class="type">float</span><span class="punct">,</span> <span class="param">percentage</span><span class="punct">:</span> <span class="type">bool</span> <span class="op">=</span> <span class="val">False</span><span class="punct">)</span> <span class="op">-&gt;</span> <span class="type">Color</span><span class="punct">:</span>
    <span class="kw">if</span> <span class="param">percentage</span><span class="punct">:</span>
        <span class="param">amount</span> <span class="op">/=</span> <span class="num">100</span>

    <span class="comment"># Scale lightness towards target bound in Oklab space</span>
    <span class="var">target_l</span> <span class="op">=</span> <span class="fn">max</span><span class="punct">(</span><span class="param">self</span><span class="punct">.</span><span class="const">__MIN_TARGET_LIGHTNESS</span><span class="punct">,</span> <span class="param">self</span><span class="punct">.</span><span class="attr">_dark</span><span class="punct">.</span><span class="attr">oklab</span><span class="punct">.</span><span class="attr">l</span><span class="punct">)</span>
    <span class="var">new_color</span> <span class="op">=</span> <span class="param">self</span><span class="punct">.</span><span class="attr">_base</span><span class="punct">.</span><span class="fn">darken</span><span class="punct">(</span><span class="fn">abs</span><span class="punct">(</span><span class="param">amount</span><span class="punct">),</span> <span class="var">target_l</span><span class="punct">)</span>

<span class="line-highlight">    <span class="comment"># Directional chroma blend in polar Oklch space</span>
    <span class="var">delta_c</span> <span class="op">=</span> <span class="punct">(</span><span class="param">self</span><span class="punct">.</span><span class="attr">_dark</span><span class="punct">.</span><span class="attr">oklch</span><span class="punct">.</span><span class="attr">c</span> <span class="op">-</span> <span class="param">self</span><span class="punct">.</span><span class="attr">_base</span><span class="punct">.</span><span class="attr">oklch</span><span class="punct">.</span><span class="attr">c</span><span class="punct">)</span> <span class="op">*</span> <span class="fn">abs</span><span class="punct">(</span><span class="param">amount</span><span class="punct">)</span></span>
    <span class="kw">return</span> <span class="type">Color</span><span class="punct">(</span>
        <span class="var">new_color</span><span class="punct">.</span><span class="attr">oklch</span><span class="punct">.</span><span class="fn">with_c</span><span class="punct">(</span>
            <span class="param">self</span><span class="punct">.</span><span class="attr">_base</span><span class="punct">.</span><span class="attr">oklch</span><span class="punct">.</span><span class="attr">c</span> <span class="op">+</span> <span class="var">delta_c</span> <span class="op">*</span> <span class="param">self</span><span class="punct">.</span><span class="attr">chroma_blend</span>
        <span class="punct">)</span>
    <span class="punct">)</span></code></pre>
      <div class="pyg-code-diagnostic">
        <span class="diag-icon">&#x2713;</span>
        <span>Type check passed: returns <code>Color</code> instance calibrated in Oklch</span>
      </div>
    </div>

    <!-- Tab 3: Graph Example -->
    <div id="pyg-tab-graph" class="pyg-tab-pane" style="display: none;">
      <div class="pyg-graph-container">
--8<-- "docs/snippets/interactive_graph.svg"
      </div>
    </div>

  </div>

  <!-- Fixed Toast Overlay Stack -->
  <div class="pyg-toast-stack" id="pyg-toast-stack" aria-live="polite">
    <div class="pyg-demo-toast toast-success" id="pyg-toast-success" role="status">
      <span class="pyg-toast-icon">&#x2713;</span>
      <span><strong>Citation Copied:</strong> Maxwell, J. C. (1860). <em>Phil. Trans. R. Soc.</em> 150, 57&ndash;84.</span>
    </div>
    <div class="pyg-demo-toast toast-error" id="pyg-toast-error" role="status">
      <span class="pyg-toast-icon">&#x2717;</span>
      <span><strong>Citation Unavailable:</strong> Remote DOI service did not respond. Please try again.</span>
    </div>
    <div class="pyg-demo-toast toast-warning" id="pyg-toast-warning" role="alert">
      <span class="pyg-toast-icon">&#x26A0;</span>
      <span><strong>Rate Limit Reached:</strong> Too many rapid citation requests. Please wait a moment.</span>
    </div>
  </div>
</div>

Explore the [API Reference](api/index.md) to learn more about the available modules, classes, and utilities.
