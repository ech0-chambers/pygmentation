import qoplots.qoplots as qoplots
from qoplots.show import show_scheme, show_scheme_wide

scheme = "twilight"

qoplots.init(scheme)
show_scheme(qoplots.Scheme)
qoplots.init(scheme, "dark")
show_scheme(qoplots.Scheme)

