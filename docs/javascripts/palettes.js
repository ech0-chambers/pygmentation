function initialize_palettes_page() {
  const display_container_element = document.getElementById("pyg-palette-display");
  if (!display_container_element) return;

  const search_input_element = document.getElementById("pyg-palette-search");
  const scheme_select_element = document.getElementById("pyg-palette-select");
  const variant_buttons = document.querySelectorAll(".pyg-palette-toggle");
  const tooltip_element = document.getElementById("pyg-swatch-tooltip");

  if (tooltip_element && tooltip_element.parentElement !== document.body) {
    document.body.appendChild(tooltip_element);
  }

  let available_schemes = [];
  let selected_scheme = "nord";
  let selected_variant = "dark";

  function get_base_path() {
    const stylesheet_link = document.querySelector('link[href*="stylesheets/pygmentation.css"]');
    if (!stylesheet_link) return "";
    return stylesheet_link.getAttribute("href").replace("stylesheets/pygmentation.css", "");
  }

  function reset_tooltip_theme() {
    if (!tooltip_element) return;
    tooltip_element.style.backgroundColor = "var(--md-default-bg-color)";
    tooltip_element.style.color = "var(--md-default-fg-color)";
    tooltip_element.style.borderColor = "var(--md-default-fg-color--lighter)";
  }

  function apply_tooltip_theme(svg_element) {
    if (!tooltip_element) return;
    const scheme_background_color = svg_element?.getAttribute("data-bg");
    const scheme_foreground_color = svg_element?.getAttribute("data-fg");

    if (scheme_background_color && scheme_foreground_color) {
      tooltip_element.style.backgroundColor = scheme_background_color;
      tooltip_element.style.color = scheme_foreground_color;
      tooltip_element.style.borderColor = scheme_foreground_color;
    } else {
      reset_tooltip_theme();
    }
  }

  async function load_palette(scheme_name, variant_name) {
    display_container_element.style.opacity = "0.5";
    try {
      const base_path = get_base_path();
      const response = await fetch(
        `${base_path}assets/palettes/${scheme_name}_${variant_name}.svg`
      );
      if (response.ok) {
        display_container_element.innerHTML = await response.text();
        const svg_element = display_container_element.querySelector("svg");
        apply_tooltip_theme(svg_element);
      } else {
        reset_tooltip_theme();
      }
    } catch (error) {
      console.error("Failed to load palette:", error);
      reset_tooltip_theme();
    } finally {
      display_container_element.style.opacity = "1";
    }
  }

  function populate_dropdown(filtered_schemes) {
    if (!scheme_select_element) return;
    scheme_select_element.innerHTML = "";
    filtered_schemes.forEach((scheme_name) => {
      const option_element = document.createElement("option");
      option_element.value = scheme_name;
      option_element.textContent = scheme_name;
      scheme_select_element.appendChild(option_element);
    });

    if (filtered_schemes.includes(selected_scheme)) {
      scheme_select_element.value = selected_scheme;
    } else if (filtered_schemes.length > 0) {
      selected_scheme = filtered_schemes[0];
      scheme_select_element.value = selected_scheme;
      load_palette(selected_scheme, selected_variant);
    }
  }

  function show_tooltip(swatch_element) {
    if (!tooltip_element) return;
    const hex_code = swatch_element.getAttribute("data-hex");
    if (!hex_code) return;

    tooltip_element.textContent = hex_code;
    const swatch_rectangle = swatch_element.getBoundingClientRect();

    tooltip_element.style.left = `${swatch_rectangle.left + swatch_rectangle.width / 2}px`;

    if (swatch_rectangle.top < 40) {
      tooltip_element.style.top = `${swatch_rectangle.bottom + 6}px`;
      tooltip_element.style.transform = "translate(-50%, 0)";
    } else {
      tooltip_element.style.top = `${swatch_rectangle.top - 6}px`;
      tooltip_element.style.transform = "translate(-50%, -100%)";
    }

    tooltip_element.style.display = "block";
  }

  function hide_tooltip() {
    if (!tooltip_element) return;
    tooltip_element.style.display = "none";
  }

  async function copy_swatch_hex(swatch_element) {
    const hex_code = swatch_element.getAttribute("data-hex");
    if (!hex_code) return;

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(hex_code);
      } else {
        const temporary_input = document.createElement("input");
        temporary_input.value = hex_code;
        document.body.appendChild(temporary_input);
        temporary_input.select();
        document.execCommand("copy");
        document.body.removeChild(temporary_input);
      }
      if (tooltip_element) {
        tooltip_element.textContent = `Copied ${hex_code}!`;
      }
    } catch (error) {
      if (tooltip_element) {
        tooltip_element.textContent = hex_code;
      }
    }
  }

  display_container_element.addEventListener("mouseover", (event) => {
    const swatch_element = event.target.closest(".pyg-palette-swatch");
    if (swatch_element) {
      show_tooltip(swatch_element);
    }
  });

  display_container_element.addEventListener("mouseout", (event) => {
    const swatch_element = event.target.closest(".pyg-palette-swatch");
    if (swatch_element) {
      hide_tooltip();
    }
  });

  display_container_element.addEventListener("click", async (event) => {
    const swatch_element = event.target.closest(".pyg-palette-swatch");
    if (swatch_element) {
      await copy_swatch_hex(swatch_element);
    }
  });

  window.addEventListener("scroll", hide_tooltip, { passive: true });

  search_input_element?.addEventListener("input", () => {
    const search_query = search_input_element.value.trim().toLowerCase();
    const matching_schemes = available_schemes.filter((scheme_name) =>
      scheme_name.toLowerCase().includes(search_query)
    );
    populate_dropdown(matching_schemes);
  });

  scheme_select_element?.addEventListener("change", () => {
    selected_scheme = scheme_select_element.value;
    load_palette(selected_scheme, selected_variant);
  });

  variant_buttons.forEach((button_element) => {
    button_element.addEventListener("click", () => {
      variant_buttons.forEach((active_button) => {
        active_button.classList.remove("active");
        active_button.classList.remove("md-button--primary");
      });
      button_element.classList.add("active");
      button_element.classList.add("md-button--primary");
      selected_variant = button_element.dataset.variant;
      load_palette(selected_scheme, selected_variant);
    });
  });

  const base_path = get_base_path();
  fetch(`${base_path}assets/data/schemes.json`)
    .then((response) => response.json())
    .then((schemes_data) => {
      available_schemes = schemes_data;
      if (available_schemes.includes("nord")) {
        selected_scheme = "nord";
      } else if (available_schemes.length > 0) {
        selected_scheme = available_schemes[0];
      }
      populate_dropdown(available_schemes);
      load_palette(selected_scheme, selected_variant);
    })
    .catch((error) => {
      console.error("Failed to load schemes list:", error);
    });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(initialize_palettes_page);
} else {
  document.addEventListener("DOMContentLoaded", initialize_palettes_page);
}
