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
