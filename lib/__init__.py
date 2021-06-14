from . import concurrency  # just the concurrency check. No actual imports
from .api import Api, get_pixels, set_pixel, handle_sane_ratelimit, Pixel
from .cli import arguments
from .kool import Fore
from .image_process import render
from .errors import *

api = Api(
    arguments.base,
    auth=arguments.auth
)


if arguments.download:
    api.get_pixels((1920, 1080)).save("./canvas.png")
    print("Canvas downloaded to ./canvas.png!")
    # Don't exit


def query_params():
    args = arguments
    if args.start_x is None or args.start_y is None:
        start_x, start_y = map(int, input("Cursor will start at: ").split(","))
    else:
        start_x = args.start_x
        start_y = args.start_y
    if args.end_x is None or args.end_y is None:
        end_x, end_y = map(int, input("Cursor will end at: ").split(","))
    else:
        end_x = args.end_x
        end_y = args.end_y

    assert end_x > start_x, "end x is smaller than start x."
    assert end_y >= start_y, "end y is smaller than start y"
    image_width = (end_x - start_x)
    image_height = (end_y - start_y)
    return start_x, start_y, end_x, end_y, image_width, image_height
