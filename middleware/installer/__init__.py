import sys

_commands = {}

_imports = [
    "run"
]


def default_imports():
    for name in _imports:
        module_name = "%s.%s" % (__name__, name)
        __import__(module_name)


def command(name, options="", description="", hidden=False):
    def wrapper(callback):
        callback.name = name
        callback.options = options
        callback.description = description
        callback.hidden = hidden
        _commands[name] = callback
        return callback

    return wrapper


@command("help", "[command]", hidden=True)
def help(args):
    if not args:
        print("Usage: middleware-apm command [options]")
        print()
        print("Type 'middleware-apm help <command>'", end="")
        print("for help on a specific command.")
        print()
        print("Available commands are:")

        commands = sorted(_commands.keys())
        for name in commands:
            details = _commands[name]
            if not details.hidden:
                print(" ", name)
    else:
        name = args[0]
        if name not in _commands:
            print("Unknown command '%s'." % name, end=" ")
            print("Type 'middleware-apm help' for usage.")
        else:
            details = _commands[name]
            print("Usage: middleware-apm %s %s" % (name, details.options))
            if details.description:
                print()
                description = details.description
                print(description)


def main() -> None:
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1]
        else:
            command = "help"

        callback = _commands[command]

    except Exception:
        print("Unknown command '%s'." % command, end="")
        print("Type 'middleware-apm help' for usage.")
        sys.exit(1)

    callback(sys.argv[2:])


default_imports()

if __name__ == "__main__":
    main()
