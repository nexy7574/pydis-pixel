import os
from typing import Optional, Any, Union

from rich.console import Console, JustifyMethod
from rich.style import Style
from rich.theme import Theme
from .cli import arguments


class CustomConsole(Console):
    LOG_LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "critical": 4}

    def log(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: Optional[Union[str, Style]] = None,
        justify: Optional[JustifyMethod] = None,
        emoji: Optional[bool] = None,
        markup: Optional[bool] = None,
        highlight: Optional[bool] = None,
        log_locals: bool = False,
        _stack_offset: int = 1,
    ) -> None:
        prefix = str(objects[0])
        if prefix.startswith("["):
            prefix = prefix[1:-1].lower()
            if prefix.replace("ing", "") in self.LOG_LEVELS:
                level = self.LOG_LEVELS[prefix.replace("ing", "")]
                if level < arguments.quiet:
                    return
        super().log(
            *objects,
            sep=sep,
            end=end,
            style=style,
            justify=justify,
            emoji=emoji,
            markup=markup,
            highlight=highlight,
            log_locals=log_locals,
            _stack_offset=_stack_offset,
        )


console = CustomConsole(
    soft_wrap=True,
    no_color=arguments.no_colour,
    force_interactive=os.getenv("FORCE_INTERACTIVE_TERMINAL", None),
    theme=Theme(
        {
            "debug": "dim i",
            "info": "",
            "warning": "bold yellow",
            "warn": "bold yellow",
            "error": "bold red",
            "critical": "bold red",
        }
    ),
    log_path=False,  # always displays console.py:33
)
