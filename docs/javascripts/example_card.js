document.addEventListener("DOMContentLoaded", () => {
  const example_card_element = document.querySelector(".pyg-example-card");
  const preview_element = document.querySelector(".pyg-preview");
  if (!preview_element) return;

  const scheme_select_element = document.getElementById("pyg-scheme-select");
  const variant_buttons = document.querySelectorAll(".pyg-button-toggle");
  const tab_buttons = document.querySelectorAll(".pyg-tab-button");
  const tab_panes = document.querySelectorAll(".pyg-tab-pane");

  const success_toast_element = document.getElementById("pyg-toast-success");
  const error_toast_element = document.getElementById("pyg-toast-error");
  const warning_toast_element = document.getElementById("pyg-toast-warning");

  const toast_elements = [
    success_toast_element,
    error_toast_element,
    warning_toast_element,
  ].filter((element) => element !== null);

  let toast_hide_timeout_id = null;
  let recent_click_timestamps = [];

  const hide_all_toasts = () => {
    if (toast_hide_timeout_id !== null) {
      clearTimeout(toast_hide_timeout_id);
      toast_hide_timeout_id = null;
    }
    toast_elements.forEach((toast_element) => {
      toast_element.classList.remove("visible");
    });
  };

  const show_toast = (target_toast_element) => {
    if (!target_toast_element) return;

    if (toast_hide_timeout_id !== null) {
      clearTimeout(toast_hide_timeout_id);
      toast_hide_timeout_id = null;
    }

    toast_elements.forEach((toast_element) => {
      if (toast_element !== target_toast_element) {
        toast_element.classList.remove("visible");
      }
    });

    if (target_toast_element.classList.contains("visible")) {
      target_toast_element.classList.remove("visible");
      void target_toast_element.offsetWidth;
    }

    target_toast_element.classList.add("visible");

    toast_hide_timeout_id = setTimeout(() => {
      target_toast_element.classList.remove("visible");
      toast_hide_timeout_id = null;
    }, 3200);
  };

  const handle_action_button_click = (button_element) => {
    button_element.style.transform = "scale(0.95)";
    setTimeout(() => {
      button_element.style.transform = "";
    }, 120);

    const current_timestamp = Date.now();
    recent_click_timestamps = recent_click_timestamps.filter(
      (timestamp) => current_timestamp - timestamp < 2200
    );
    recent_click_timestamps.push(current_timestamp);

    if (recent_click_timestamps.length >= 3) {
      show_toast(warning_toast_element);
    } else {
      const selected_toast_element =
        Math.random() < 0.65 ? success_toast_element : error_toast_element;
      show_toast(selected_toast_element);
    }
  };

  const action_buttons = document.querySelectorAll(
    ".pyg-demo-article .pyg-demo-button"
  );
  action_buttons.forEach((button_element) => {
    button_element.addEventListener("click", () => {
      handle_action_button_click(button_element);
    });
  });

  scheme_select_element?.addEventListener("change", (event) => {
    const selected_scheme = event.target.value;
    example_card_element?.setAttribute("data-scheme", selected_scheme);
    preview_element.setAttribute("data-scheme", selected_scheme);
  });

  variant_buttons.forEach((button_element) => {
    button_element.addEventListener("click", () => {
      variant_buttons.forEach((active_button_element) => {
        active_button_element.classList.remove("active");
        active_button_element.classList.remove("md-button--primary");
      });
      button_element.classList.add("active");
      button_element.classList.add("md-button--primary");
      const selected_variant = button_element.dataset.variant;
      example_card_element?.setAttribute("data-variant", selected_variant);
      preview_element.setAttribute("data-variant", selected_variant);
    });
  });

  tab_buttons.forEach((button_element) => {
    button_element.addEventListener("click", () => {
      tab_buttons.forEach((active_button_element) => {
        active_button_element.classList.remove("active");
      });
      button_element.classList.add("active");

      const target_tab = button_element.dataset.tab;
      if (target_tab !== "webpage") {
        hide_all_toasts();
      }

      tab_panes.forEach((pane_element) => {
        pane_element.style.display =
          pane_element.id === `pyg-tab-${target_tab}` ? "block" : "none";
      });
    });
  });
});
