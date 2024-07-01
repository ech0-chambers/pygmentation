import pygmentation.pygmentation as pygmentation
from pygmentation.show import show_scheme, show_scheme_wide

scheme = "twilight"

pygmentation.init(scheme)
show_scheme(pygmentation.Scheme)
pygmentation.init(scheme, "dark")
show_scheme(pygmentation.Scheme)

