# Robbed straight from v1

from PIL import Image
from io import BytesIO
import sys
from typing import Dict, Tuple, List


PIXEL_DATA = List[Tuple[int, int, Tuple[int, int, int, int]]]


def rgba_to_hex(r: int, g: int, b: int, a: int, *, rgb_only: bool = False) -> str:
    """
    Converts an rgba value to a hex value.

    :param r:
    :param g:
    :param b:
    :param a:
    :param rgb_only:
    :return:
    """
    _hex = ""
    _hex += hex(r).replace("0x", "").zfill(2)
    _hex += hex(g).replace("0x", "").zfill(2)
    _hex += hex(b).replace("0x", "").zfill(2)
    if not rgb_only:
        _hex += hex(a).replace("0x", "").zfill(2)
    return _hex


def map_pixels(array: list, rgba: bool = False):
    pixels_map = {}
    for e in array:
        r, g, b, a = e[2]
        _hex = ""
        _hex += hex(r).replace("0x", "").zfill(2)
        _hex += hex(g).replace("0x", "").zfill(2)
        _hex += hex(b).replace("0x", "").zfill(2)
        if rgba:
            _hex += hex(a).replace("0x", "").zfill(2)
            pixels_map[(e[0], e[1])] = _hex
        else:
            pixels_map[(e[0], e[1])] = _hex
    return pixels_map


def get_pixels(img) -> PIXEL_DATA:
    """
    Fetches an array of [x, y, (r, g, b, a)] in the image, with x, y being the x,y co-ords and rgb being the rgb values.

    :param img: the PIL.Image
    :return: List[Tuple[int, int, Tuple[int, int, int, int]]]
    """
    pixels = []
    for y in range(img.height):
        for x in range(img.width):
            pixels.append((x, y, img.getpixel((x, y))))
    return pixels


def convert_bytes(image_data: bytes) -> Image.Image:
    """
    Converts the bytes into a PIL.Image object.

    :param image_data:
    :return:
    """
    return Image.open(BytesIO(image_data))


def render(
    image_width: int, image_height: int, image_bytes: bytes
) -> Tuple[Image.Image, Dict[Tuple[int, int], str], List[Tuple[int, int, Tuple[int, int, int, int]]]]:
    pil_image: Image.Image = Image.open(BytesIO(image_bytes))  # open the image into an Image object
    pil_image: Image.Image = pil_image.convert("RGBA")
    pil_image: Image.Image = pil_image.resize((image_width, image_height), Image.NEAREST)  # Resize it to the cursor

    pixels_array = get_pixels(pil_image)  # Gets the raw pixel data for the mapping
    pixels_map: Dict[Tuple[int, int], str] = map_pixels(pixels_array, True)  # a mapping of (x, y): hex
    return pil_image, pixels_map, pixels_array
