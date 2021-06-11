try:
    # This is in a try/except because its safe to assume people have requests, its probable they have mpl/pil,
    # but colorama isn't exactly a must-have for most projects.
    from colorama import Fore, init

    init(autoreset=True)
except ImportError:
    print("Colorama is not installed. Your console won't look cool!")
    init = None

    class _Fore:
        def __getattr__(self, item):
            return ""

    Fore = _Fore()

__all__ = ("Fore",)


def _print(*args, verbose: bool = ..., **kwargs):
    from .cli import arguments
    if verbose is ...:
        verbose = any(
            (x in kwargs.get("sep", " ").join(map(str, args)) for x in ("[VERBOSE]", "[DEV]", "[DEBUG]"))
        )
    if verbose and not arguments.verbose:
        return
    print(*args, **kwargs)
