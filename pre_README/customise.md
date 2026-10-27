
You can register custom colour schemes in two ways:

### 1. User Configuration File

`pygmentation` automatically checks for user-defined schemes in `~/.config/pygmentation/color_schemes.json`. Schemes placed here are discovered alongside built-in themes:

```json
{
  "my_custom_theme": {
    "foreground": "#F8F8F2",
    "background": "#282A36",
    "accents": [
      "#FF79C6",
      "#BD93F9",
      "#50FA7B",
      "#FFB86C"
    ]
  }
}
```

These schemes must define a `foreground` and `background` colour, and an `accents` list.

### 2. Programmatic Registration

Register or unregister schemes dynamically at runtime (registered schemes are *not* saved to the custom schemes file):

```python
from pygmentation import registry

registry.register("my_theme", {
    "foreground": "#FFFFFF",
    "background": "#111111",
    "accents": ["#FF0055", "#00FFAA"]
})

scheme = registry.get("my_theme", "dark")
```

---

## Development & Quality Gates

The `pygmentation` test suite and linters enforce strict typing and code style:

```bash
# Run full unit test suite:
pytest

# Check linting and code formatting:
ruff check src tests

# Static type checking:
mypy src
```

