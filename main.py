#!/usr/bin/env python3
import datetime
import os
import sys
from io import BytesIO
from typing import Dict, Tuple

import requests
from PIL import Image

from lib.api import get_pixels, set_pixel, handle_sane_ratelimit
from lib import Fore, arguments as args

if not args.auth:
    if not os.path.exists("./auth.txt"):
        print(Fore.RED + "You have not provided an authentication token. Please read the README.")
        sys.exit(4)

    with open("./auth.txt") as auth:
        token = auth.read().strip()
else:
    token = args.auth

base = args.base
print(Fore.LIGHTBLUE_EX + "[RATELIMIT] " + Fore.LIGHTGREEN_EX + "Syncing ratelimit...")
handle_sane_ratelimit(requests.head(base + "/set_pixel", headers={"Authorization": "Bearer " + token}))
# Handling the ratelimit here will sync our cooldown to zero.

canvas_size_response = requests.get(base + "/get_size").json()
canvas_width = int(canvas_size_response["width"])
canvas_height = int(canvas_size_response["height"])

print(f"{Fore.MAGENTA}[CANVAS] {Fore.WHITE}(W:H) {canvas_width}:{canvas_height}")

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
image_width = (end_x - start_x) - 1  # zero-indexing.
image_height = (end_y - start_y) - 1

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
pilImage: Image = pilImage.resize((image_width, image_height))  # Resize it to the cursor border
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


def paint():
    """
    Handles painting on the canvas.

    This is the main runtime, only in a function to allow for easier looping.
    """
    painted = 0

    print(
        Fore.YELLOW + "[CURSOR] ",
        Fore.CYAN + "Beginning paint. It will likely finish at",
        (datetime.datetime.now() + datetime.timedelta(seconds=len(pixels_array))).strftime("%X"),
    )
    for x, y in pixels_map.keys():
        cursor = (x + start_x, y+start_y)
        # noinspection PyTypeChecker
        try:
            colour = pixels_map[(x, y)]
        except KeyError:
            if args.verbose:
                print(Fore.RED + "[DEBUG] {} is not in colour map? Going to continue.".format(cursor))
                continue
            else:
                raise
        if not args.quiet:
            print(Fore.YELLOW + "[CURSOR] " + Fore.LIGHTYELLOW_EX + "Painting {} #{}.".format(cursor, colour))
        status = set_pixel(*cursor, colour=colour, token=token, base=base)
        painted += 1
        pct = round((painted / len(pixels_array)) * 100, 2)
        if status == 200 and not args.quiet:
            print(Fore.YELLOW + "[CURSOR] " + Fore.LIGHTGREEN_EX + "Painted {} #{}. {}% done.".format(cursor,
                                                                                                      colour, pct))
    print(Fore.YELLOW + "[CURSOR] ", Fore.LIGHTGREEN_EX + "Done!")


if args.loop is not None:
    if isinstance(args.loop, bool):
        print("Running \N{infinity} times.")
        while True:
            paint()
    if isinstance(args.loop, int):
        print("Running", args.loop, "times.")
        for i in range(args.loop):
            try:
                paint()
            except Exception:
                print(f"Exception in iteration {i}:", file=sys.stderr)
                raise
else:
    print("Running once.")
    paint()
