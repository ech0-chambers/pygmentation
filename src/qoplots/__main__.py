

if __name__ == "__main__":
    from .qoplots import init, show_scheme
    import sys
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: qoplots [scheme] [variant]")
        quit()
    if len(args) == 1:
        init(args[0])
        show_scheme(name = f"{args[0]} (light)")
        init(args[0], "dark")
        show_scheme(name = f"{args[0]} (dark)")
    if len(args) == 2:
        if args[1].lower() == "both":
            init(args[0])
            show_scheme(name = f"{args[0]} (light)")
            init(args[0], "dark")
            show_scheme(name = f"{args[0]} (dark)")
        elif args[1].lower() == "save":
            init(args[0])
            show_scheme(name = f"{args[0]} (light)", save = True)
            init(args[0], "dark")
            show_scheme(name = f"{args[0]} (dark)", save = True)
        else:
            init(args[0], args[1])
            show_scheme(name = f"{args[0]} ({args[1]})")
    if len(args) == 3:
        if args[2].lower() == "save":
            init(args[0], args[1])
            show_scheme(name = f"{args[0]} ({args[1]})", save = True)
        else:
            print("Usage: qoplots [scheme] [variant] [save]")
            quit()