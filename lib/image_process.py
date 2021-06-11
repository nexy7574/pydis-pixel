from .cli import arguments as args
from .kool import Fore
from PIL import Image
import requests
from io import BytesIO
import sys
from .api import get_pixels
from typing import Dict, Tuple


def render(image_width: int, image_height: int):
    if args.image is None:
        image_path = input("Image path (provide URL for download): ")
    else:
        image_path = str(args.image)  # convert to string for the below startswith
    if image_path.startswith("http"):  # this is an image to download. send a web request.
        image_response = requests.get(image_path)
        assert image_response.headers["Content-Type"].startswith("image/"), "Incorrect image type."
        image_bytes: bytes = image_response.content
    else:
        with open(image_path, "rb") as file:
            image_bytes: bytes = file.read()

    pilImage: Image = Image.open(BytesIO(image_bytes))  # open the image into an Image object
    pilImage: Image = pilImage.convert("RGB")  # convert it to RGB (none of that RGBA crap)
    pilImage: Image = pilImage.resize((image_width, image_height), Image.NEAREST)  # Resize it to the cursor border
    if args.preview_paint:
        pilImage.save("./preview.png")
        print("Preview saved. See: preview.png")
        sys.exit(0)

    pixels_array = get_pixels(pilImage)  # Gets the raw pixel data for the mapping
    pixels_map: Dict[Tuple[int, int], str] = {}  # a mapping of (x, y): hex
    for e in pixels_array:
        r, g, b, *_ = e[2]
        if args.verbose:
            print(Fore.RED + "[DEBUG] " + Fore.LIGHTBLACK_EX + "R: {} G: {} B: {} _: {}".format(r, g, b, _))
        _hex = ""
        _hex += hex(r).replace("0x", "").zfill(2)
        _hex += hex(g).replace("0x", "").zfill(2)
        _hex += hex(b).replace("0x", "").zfill(2)
        pixels_map[(e[0], e[1])] = _hex
        if args.verbose:
            print(Fore.RED + "[DEBUG] X: {} Y: {} HEX: {}".format(e[0], e[1], _hex))
    return pilImage, pixels_map, pixels_array
