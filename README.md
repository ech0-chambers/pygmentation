<style>
.swatch {
    /* height: 1em; */
    /* width: 1.5cm; */
    display: inline-block;
    margin-inline-start: 0.5ch;
    padding-inline: 2ch;
    font-family: monospace;
    font-weight: bold;
    font-size: 0.9em;
}

td, th {
    text-align: center;
}

div.split{
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
    margin: 1em;
    flex-wrap: wrap;
}
div.split > * {
    min-width: 5in;
}
</style>

# qoplots 
A quality-of-life package for colour schemes and matplotlib plots.

**Note:** The UK spelling of "colour" is used throughout the `qoplots` package.

- [Requirements](#requirements)
- [Colour Schemes](#colour-schemes)
- [Colour Aliases](#colour-aliases)
- [Variation Generation](#variation-generation)
- [Usage](#usage)
    - [Python Library](#python-library)
        - [`ColourScheme` object](#colourscheme-object)
        - [`ColourFamily` Object](#colourfamily-object)
        - [`Colour` Object](#colour-object)
    - [Command Line Interface](#command-line-interface)
        - [`show`](#show)
        - [`save`](#save)
        - [`write`](#write)

## Requirements

`qoplots` relies on the following python packages:
 - `numpy`
 - `matplotlib`
 - `rich`

## Colour Schemes

Predominantly, `qoplots` is a library for handling colour schemes. Each scheme consists of a background colour family, a foreground colour family, and some number of accent and (optionally) surface colour families. Each colour family consists of six variants: the 'base' colour (the colour which is supplied directly), and 5 automatically generated variants. The exact generation of these variants is discussed in the later sections.





For example, in the Nord colour scheme - [https://www.nordtheme.com/](https://www.nordtheme.com/) - one of the accent colours is this red: <span class="swatch" style = "background: #BF616A; color: #ECEFF4;">#BF616A</span>. This is the 'base' for this colour family. There are then 5 variants, labelled `1` to `5`, which are as follows:
- `1`: <span class="swatch" style = "background: #DBA5AA; color: #2E3440;">#DBA5AA</span>
- `2`: <span class="swatch" style = "background: #CD838A; color: #2E3440;">#CD838A</span>
- `3`: <span class="swatch" style = "background: #983E46; color: #ECEFF4;">#983E46</span>
- `4`: <span class="swatch" style = "background: #7E333A; color: #ECEFF4;">#7E333A</span>
- `5`: <span class="swatch" style = "background: #63282E; color: #ECEFF4;">#63282E</span>

Although the exact shades differ depending on the scheme (as discussed in the later sections), they will always be organised such that `1` has the most contrast with the background colour (which is in this case <span class="swatch" style = "background: #2E3440">#2E3440</span>) and `5` will have the least contrast. For dark colour schemes, this means that they are ordered from light to dark; for light schemes, from dark to light.

As a full scheme, this gives access to a wide range of variations on each colour. Again taking the Nord theme as an example, all available colours and variants are shown in the image below, which is the output from running the command `qoplots show nord dark`:

![Output from `qoplots show nord dark`](nord.svg)

## Colour Aliases

While colours are always available via their index (for example, as `scheme.accents[0].base`), some colours are also available under aliases. When a scheme is loaded, `qoplots` checks all accent colours to find which is the closest to a set of standard colours. These are as follows, with the reference hue in brackets followed by the reference colour for light and dark schemes respectively:

| Name    | Hue Angle | Reference (Light)                                          | Reference (Dark)                                           |
|---------|-----------|------------------------------------------------------------|------------------------------------------------------------|
| Red     | 0&deg;    | <span class="swatch" style = "background: #bd0000; color: #ffffff;">#BD0000</span> | <span class="swatch" style = "background: #d52a2a; color: #ffffff;">#D52A2A</span> |
| Orange  | 30&deg;   | <span class="swatch" style = "background: #bd5f00; color: #ffffff;">#BD5F00</span> | <span class="swatch" style = "background: #d5802a; color: #000000;">#D5802A</span> |
| Yellow  | 50&deg;   | <span class="swatch" style = "background: #bd9d00; color: #000000;">#BD9D00</span> | <span class="swatch" style = "background: #d5b82a; color: #000000;">#D5B82A</span> |
| Green   | 120&deg;  | <span class="swatch" style = "background: #00bd00; color: #000000;">#00BD00</span> | <span class="swatch" style = "background: #2ad52a; color: #000000;">#2AD52A</span> |
| Cyan    | 180&deg;  | <span class="swatch" style = "background: #00bdbd; color: #000000;">#00BDBD</span> | <span class="swatch" style = "background: #2ad5d5; color: #000000;">#2AD5D5</span> |
| Blue    | 240&deg;  | <span class="swatch" style = "background: #0000bd; color: #ffffff;">#0000BD</span> | <span class="swatch" style = "background: #2a2ad5; color: #ffffff;">#2A2AD5</span> |
| Purple  | 270&deg;  | <span class="swatch" style = "background: #5e00bd; color: #ffffff;">#5E00BD</span> | <span class="swatch" style = "background: #802ad5; color: #ffffff;">#802AD5</span> |
| Magenta | 300&deg;  | <span class="swatch" style = "background: #bd00bd; color: #ffffff;">#BD00BD</span> | <span class="swatch" style = "background: #d52ad5; color: #000000;">#D52AD5</span> |

Four additional aliases are available, 
- Error (alias for red)
- Warning (alias for yellow)
- Success (alias for green)
- Info (alias for blue)

All aliases will be assigned, although some aliases may be assigned to the same colour (for example in the Nord theme, `purple` and `magenta` both refer to the same colour: <span class="swatch" style = "background: #B48EAD; color: #2E3440;">#B48EAD</span>). Aliases are then accessible by (for example) `scheme.red.base` or `scheme.error.base`.

Colour similarity is determined using the CIE Delta E 2000 Color-Difference algorithm; this involves converting the colour (provided in hex format) first into the L\*ab colour space, then using the CIEDE2000 algorithm to determine a perceptually uniform distance between the colours. Most colour spaces (such as RGB, HSL, or hsb) are not perceptually uniform. In the HSL colour space, colours are expressed as a hue (expressed as an angle in degrees), saturation (expressed as a percentage), and lightness (expressed as a percentage). "Pure" colours (such as `#ff0000` in the RGB colour space) have a saturation of 100% and a lightness of 50%. 

However, the perceived visual change between a hue of 100&deg; (<span class="swatch" style = "background: hsl(100, 100%, 50%); color: #000000;">#55ff00</span>) and a hue of 130&deg; (<span class="swatch" style = "background: hsl(130, 100%, 50%); color: #000000;">#00ff2b</span>) is clearly significantly less than the change between a hue of 260&deg; (<span class="swatch" style = "background: hsl(260, 100%, 50%);">#5500ff</span>) and a hue of 290&deg; (<span class="swatch" style = "background: hsl(290, 100%, 50%); color: #ffffff">#d400ff</span>), despite the fact that the separation in the HSL colour space is the same. The L\*ab colour space is designed to be perceptually uniform, and it is much closer to achieving this goal than the RGB or HSL colour spaces. However, it is not actually perceptually uniform, so the CIEDE2000 algorithm includes a number of corrections to account for this. This will never be perfect, but it produces noticeably better results (even for such a relatively simple task) than directly using RGB (as many projects do) or other colour spaces.

## Variation Generation

Each base colour has five colour variants generated. These are designed to usually mimic the colour variations in Microsoft Office, although there are some exceptions. The generation is identical for light and dark colour schemes, but inverted. The process will be explained for a light theme (i.e, one in which the background colour is significantly lighter than the foreground colour). For dark themes, any reference to "lighter" or "darker" should be reversed. Variants are *always* arranged such that the 1<sup>st</sup> variant has the most contrast with the background colour, and the 5<sup>th</sup> variant has the least contrast (assuming the background is sufficiently light or sufficiently dark).

Most base colours will have two darker variants and three lighter variants. Variants are calculated in the HSL colour space. Hue and saturation are (usually) the same for the variants as the base colour, with only the lightness changing. The five variants are (as numbered):
- `1`: 50% darker
- `2`: 25% darker
- `3`: 40% lighter
- `4`: 60% lighter
- `5`: 80% lighter

Exactly what is meant by "lighter" and "darker" is discussed in the next section.

Some colours are determined to be too light or too dark to have the full range of variants (again, this is to mimic the behaviour of Microsoft Office). In the Nord theme shown above, this is the case for the foreground and background colours, as well as surface colours 1 and 2. If a base colour has a lightness of $l>80\%$, it is deemed too light to have lighter variants. In this case, it is instead given 5 darker variants:
- `1`: 90% darker
- `2`: 75% darker
- `3`: 50% darker
- `4`: 25% darker
- `5`: 10% darker

Similarly, if a base colour has a lightness of $l<20\%$, it is deemed too dark to have darker variants. In this case, it is instead given 5 lighter variants:
- `1`: 10% lighter
- `2`: 25% lighter
- `3`: 50% lighter
- `4`: 75% lighter
- `5`: 90% lighter

Finally, some base colours may have their hue and saturation adjusted in the variants. If the hue and saturation of the base colour is close enough to the background colour (foreground colour for dark schemes), then the lighter variants will have their hue, saturation, and lightness all shifted towards the background colour (still by the same percentages). Similarly, if the hue and saturation of the base colour is close enough to the foreground colour (background colour for dark schemes), then the darker variants will have their hue, saturation, and lightness all shifted towards the foreground colour (again, by the same percentages). This produces very similar results, but gives a slightly more aesthetically pleasing result for some colours, especially when the background colour has a noticeable hue.

### "Lighter" and "Darker" colours

The phrase "$20\%$ lighter" is ambiguous. Here, it means that the new colour is $20\%$ closer to the maximum lightness. This means that a colour will only ever reach maximum lightness if it is "lightened" by $100\%$. Most of the time, this means that for a colour with lightness $l$, the colour $x\%$ lighter will have lightness:
$$l_{\text{new}} = l + x \times (100 - l)$$

For darker colours, the concept is the same: the colour $x\%$ darker will have lightness:
$$l_{\text{new}} = l - x \times (l - 0\%)$$

However, the "maximum" lightness is not always $100\%$ in this context. When calculating the lighter variants, the "maximum" lightness is instead the larger value out of $80\%$ and the lightness of the background colour. Similarly, when calculating the darker variants, the "minimum" lightness is the smaller value out of $20\%$ and the lightness of the foreground colour. This keeps the colour variants within the range of the background and foreground colours, respectively, provided the background colour is sufficiently light and the foreground colour is sufficiently dark. 

For dark themes, this process is the same but with the foreground and background colours reversed.

For example, with the dark version of the Nord theme, the red colour is shown in the table below, with and without the background colour taken into account:

| Variant | Modification   | Basic | With Foreground/Background |
| ------- | -------------- | ----- | -------------------------- |
| 1       | $50\%$ lighter | <span class="swatch" style = "background: #DFB0B4; color: #2E3440;">#DFB0B4</span> | <span class="swatch" style = "background: #DBA5AA; color: #2E3440;">#DBA5AA</span> |
| 2       | $25\%$ lighter | <span class="swatch" style = "background: #CF898F; color: #2E3440;">#CF898F</span> | <span class="swatch" style = "background: #CD838A; color: #2E3440;">#CD838A</span> |
| base    | -              | <span class="swatch" style = "background: #BF616A; color: #ECEFF4;">#BF616A</span> | <span class="swatch" style = "background: #BF616A; color: #ECEFF4;">#BF616A</span> |
| 3       | $40\%$ darker  | <span class="swatch" style = "background: #7B3239; color: #ECEFF4;">#7B3239</span> | <span class="swatch" style = "background: #983E46; color: #ECEFF4;">#983E46</span> |
| 4       | $60\%$ darker  | <span class="swatch" style = "background: #522126; color: #ECEFF4;">#522126</span> | <span class="swatch" style = "background: #7E333A; color: #ECEFF4;">#7E333A</span> |
| 5       | $80\%$ darker  | <span class="swatch" style = "background: #291113; color: #ECEFF4;">#291113</span> | <span class="swatch" style = "background: #63282E; color: #ECEFF4;">#63282E</span> |

This usually produces more aesthetically pleasing variations, but with slightly less contrast. However, clamping the values to $20\%$ and $80\%$ helps to ensure that the variants are still distinct from the background and foreground colours, respectively.

## Usage

`qoplots` can be used as a python library or via the command line interface. 

### Python Library

The usual use of `qoplots` will be to set default styling for `matplotlib` plots. To be safe, `qoplots` should be imported before `matplotlib`:

```python
import qoplots.qoplots as qp
qp.init("rose_pine", "light")
import matplotlib.pyplot as plt

# Continue as normal. No further changes to matplotlib are required.
```

The function `qp.init` takes three arguments: the name of the colour scheme, the type (`"light"` or `"dark"`), and the target document type (`"report"` or `"presentation"`). The document type will determine certain aspects of the styling, such as the aspect ratio, the font size, default text and axis colour, and so on. Examples are seen below for the `rose_pine` colour scheme. Note that no additional styling was specified. For the `"report"` style, the background is transparent where possible, with only the plot area having a solid background. 

<div class="split">

![Report style](sample_report.svg)

![Presentation style](sample_presentation.svg)

</div>

Within python, the current colour scheme is available via the `qp.get_scheme()` function. This returns a `ColourScheme` object. 

#### `ColourScheme` object

Notable methods and properties are listed below:
- Methods:
    - `get_closest_color(color: str | Color, accents_only: bool = False) -> ColorFamily` This takes a test colour (as either a hex RGB string or a `Color` object) and returns the closest base colour in the scheme. Optionally, this can be restricted to only search the accent colours.
    - `to_latex() -> str` Returns a string containing appropriate LaTeX code to define the colour scheme. For the exact format of this string, see the section below on the command line interface.
    - `to_css() -> str` Returns a string containing appropriate CSS code to define the colour scheme. For the exact format of this string, see the section below on the command line interface.
    - `to_javascript() -> str` Returns a string containing appropriate JavaScript code to define the colour scheme as an object. For the exact format of this string, see the section below on the command line interface.
- Properties:
    - `foreground: ColourFamily` The foreground colour family.
    - `background: ColourFamily` The background colour family.
    - `accents: list[ColourFamily]` The list of accent colour families.
    - `surfaces: list[ColourFamily]` The list of surface colour families. This may be empty.
    - `distinct: list[ColourFamily]` A list containing a subset of the accent colours. Colours which are deemed too similar to another accent colour are filtered out.
    - `colours: list[ColourFamily]` A list containing all colour families within the scheme, including the foreground, background, accents, and surfaces.
    - `red: ColourFamily` The closest accent colour to red.
    - Similar properties exist for each of `orange`, `yellow`, `green`, `cyan`, `blue`, `purple`, and `magenta`.
    - `error: ColourFamily` Alias for `red`.
    - `warning: ColourFamily` Alias for `yellow`.
    - `success: ColourFamily` Alias for `green`.
    - `info: ColourFamily` Alias for `blue`.


#### `ColourFamily` Object
A `ColourFamily` object contains the base colour and all variants. Notable methods and properties are listed below:
- Methods:
    - `to_latex() -> str` Returns a string containing appropriate LaTeX code to define the colour family. 
    - `to_css() -> str` Returns a string containing appropriate CSS code to define the colour family.
    - `to_javascript() -> str` Returns a string containing appropriate JavaScript code to define the colour family as an object.
- Properties:
    - `base: Color` The base colour.
    - `_1: Color` to `_5: Color` The variants, as described above.
    - `lightest: Color` Returns the lightest variant, regardless of whether the `Colour` is in the context of a light or dark scheme.
    - `darkest: Color` Returns the darkest variant, regardless of whether the `Colour` is in the context of a light or dark scheme.
    - `hex: str` Returns the hex code for the base colour, without the leading `#`.
    - `css: str` Returns the hex code for the base colour, with the leading `#`.
The `ColourFamily` object is also subscriptable, so a colour variant can be accessed via `colour_family[1]` which is equivalent to `colour_family._1`. `colour_family[0]` is equivalent to `colour_family.base`.


#### `Colour` Object
A `Colour` object contains a single colour, as well as methods for converting between colour spaces and for comparing colours. Notable methods and properties are listed below:
- Methods:
    - `lighten(amount: float, in_place: bool = False, target_lightness: float = 1) -> Colour` Lightens the current colour by the specified amount, as described above. If `amount` is between 0 and 1, this is assumed to mean `amount * 100%`. If `in_place` is true, the current colour is modified; otherwise, a new `Colour` object is returned.
    - `darken(amount: float, in_place: bool = False, target_lightness: float = 0) -> Colour` Darkens the current colour by the specified amount, as described above. If `amount` is between 0 and 1, this is assumed to mean `amount * 100%`. If `in_place` is true, the current colour is modified; otherwise, a new `Colour` object is returned.
    - `move_to_colour(other: Colour, amount: float, in_place: bool = False) -> Colour` Moves the current colour towards the specified colour by the specified amount, in the HSL colour space. If `amount` is between 0 and 1, this is assumed to mean `amount * 100%`. If `in_place` is true, the current colour is modified; otherwise, a new `Colour` object is returned.
    - `hue_diff(other: Colour) -> float` Returns the difference in hue between the current colour and the specified colour, in degrees, accounting for the periodic nature of the hue angle.
    - `is_lighter_than(other: Colour) -> bool` Returns true if the current colour is lighter than the specified colour.
    - `is_darker_than(other: Colour) -> bool` Returns true if the current colour is darker than the specified colour.
    - `distance_to(other: Colour) -> float` Returns the distance between the current colour and the specified colour using the CIEDE2000 algorithm.
- Properties:
    - Properties exist to retrieve the colour in any of the following colour spaces/formats. All properties are read/write -- setting the property in any colour space will change the colour of the `Colour` object. Properties also exist for each component of these colour spaces, occasionally with aliases. These are also read/write.
        - `rgb`
            - `r`, `g`, `b`
        - `hsl`
            - `h`, `s`, `l`
        - `hsv`
            - `h_hsv`, `s_hsv`, `v` (alias `v_hsv`)
        - `xyz`
            - `x`, `y`, `z`
        - `lab`
            - `l_lab`, `a` (alias `a_lab`), `b` (alias `b_lab`)
        - `hex`
        - `css`

### Command Line Interface

`qoplots` can be used as a command line tool when run as a module (with `python3 -m qoplots`). There are three main commands: `show`, `save`, and `write`. These will be described fully below. `show` will display a given scheme in the terminal -- this is useful for quickly checking what colours are available in a given scheme. `save` will act the same as `show` but additionally saves the output to an SVG file. `write` will write the colour scheme to a file in a given format for use outside of python.

For all commands, if the scheme name is not recognised `qoplots` will search the available schemes for similar names, and present a list of the closest matches. It will then wait for confirmation from the user. Unless you are certain that the scheme name is correct, do not assume that `qoplots` will exit without user input.

*In the examples below, the command is shown simply as `qoplots`, not `python3 -m qoplots`. This is for brevity, but an alias can be created to shorten the command if desired.*

#### `show`

`qoplots show` takes one required argument, the name of the colour scheme to display. This can be followed by an optional argument, the type of colour scheme to display (either `light`, `dark`, or `both`). The default is to display both the light and dark variants. This is rendered using the `rich` library, and requires a minimum terminal width of 56 characters to render correctly. It also requires your terminal emulator to support full colour. For example, the output shown in the first section for the Nord scheme would be produced by:
```bash
qoplots show nord dark
```

#### `save`

`qoplots save` takes the same arguments as `show`, but additionally takes an output file name. This is passed by the `-f` or `--filename` flag, which is required. If both the light and dark variants are to be saved, the file name will be adjusted to include the type of colour scheme (otherwise, it is used directly with no changes). For example, the following command will save the light and dark variants of the Nord scheme to `nord_light.svg` and `nord_dark.svg` respectively:
```bash
qoplots save -f nord.svg nord
```

The target file *must* be an SVG file. It is saved via the python `rich` library, so is again dependent on your terminal emulator as it is effectively recording the output of `qoplots show` and saving it to a file.

#### `write`

`qoplots write` takes up to four arguments:
- `-f` or `--filename`: The name of the file to write to. If both light and dark variants are to be written, the filename will be bodified to include `_light` and `_dark`. This is required.
- `-t` or `--type`: The type of file to write. If provided, this should be one of `css`, `js`, or `latex`. If not provided, qoplots will attempt to infer this from the filename.
- `scheme_name` (positional): The name of the scheme to write. This is required.
- `scheme_type` (positional): If provided, this should be one of `light`, `dark`, or `both` (default). Writes only the specified type of scheme. If not provided, writes both light and dark variants.

A minimal example would be:
```bash
qoplots write -f nord.css nord
```

This would produce two files, `nord_light.css` and `nord_dark.css`, containing the light and dark variants of the Nord scheme respectively. The exact format of the output is described below.

A second example would be:
```bash
qoplots write -f "ctp.txt" -t latex catppuccin dark
```

This would produce a single file `ctp.txt` containing the dark variant of the Catppuccin scheme in LaTeX format ([https://github.com/catppuccin/catppuccin](https://github.com/catppuccin/catppuccin)). The file extension is not used to determine the output format, so the file name can be anything. The output format is determined by the `-t` or `--type` flag, which is required if the file name does not contain a recognised extension.

## Output Formats

### LaTeX

The LaTeX output is a file containing valid LaTeX markup to define all colours and aliases of the scheme with the `xcolor` package. The foreground colour will be called `ForegroundColour`, and the background colour will be called `BackgroundColour`. The accent colours are labelled numerically as `Accent1`, `Accent2` etc, and the surface colours (if any) are labelled similarly: `Surface1` etc. The aliases are available under their capitalised names: `Red`, `Error` etc. The capitalisation is to avoid conflicts with the standard LaTeX colours.

Variants are available by appending `_1` to `_5` to each colour name or alias. For example, `Blue_5` is the lightest variant of the blue colour, and `Error_1` is the darkest variant of the red colour (in a light theme).

### CSS

The css output is a file containing css variable declarations. They are not enclosed in any style declaration, and so are not on their own a valid css file. The foreground colour will be defined as `--clr-foreground`, the background colour as `--clr-background`, and the accent colours as `--clr-accent1` etc. The surface colours (if any) are labelled similarly: `--clr-surface1` etc. The aliases are available under their names, such as `--clr-red`, `--clr-error` etc.

Variants are available by appending `-1` to `-5` to each colour name or alias. For example, `--clr-blue-5` is the lightest variant of the blue colour, and `--clr-error-1` is the darkest variant of the red colour (in a light theme).

### JavaScript

The JavaScript output is a file containing the javascript code necessary to define a single object `colours` containing all colours and aliases as properties. The foreground colour will be defined as `colours.foreground`, the background colour as `colours.background`. Accent colours are defined as both `colours.accent1` etc, and as part of the array `colours.accents` (with surfaces defined in a similar way).

Each colour is also an object which contains the properties `base` and `1` to `5`. Each of these gives the colour as a hex string, with the leading `#`. Aliases are defined with references, not copies.