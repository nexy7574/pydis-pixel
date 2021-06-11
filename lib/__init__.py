from . import concurrency  # just the concurrency check. No actual imports
from .api import Api, get_pixels, set_pixel, handle_sane_ratelimit
from .cli import arguments
from .kool import Fore
from .image_process import render
from .errors import *

api = Api(
    arguments.base,
    auth=arguments.auth
)


if arguments.download_canvas:
    api.get_pixels((1920, 1080)).save("./canvas.png")
    print("Canvas downloaded to ./canvas.png!")
    # Don't exit
