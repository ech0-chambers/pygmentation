
`pygmentation` requires **Python >= 3.11**.

Core package dependencies are strictly limited to `numpy` and `rich`. Matplotlib integration is packaged as an optional extra. 

```bash
# Core package (colour models, schemes, exporters, and CLI):
pip install pygmentation

# With Matplotlib publication styling and font discovery:
pip install "pygmentation[plots]"

# For development and testing (pytest, ruff, mypy):
pip install "pygmentation[dev]"
```

When installed, the `pygmentation` command-line executable is automatically added to your system `PATH`.
