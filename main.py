#!/usr/bin/env python3
import datetime
import sys
import os
from typing import Dict, Tuple, List
import requests
from PIL import Image
from io import BytesIO
from api import getPixels, resizeOption, set_pixel, handle_sane_ratelimit
from kool import Fore

if not os.path.exists("./auth.txt"):
    print(Fore.RED + "You have not provided an authentication token. Please read the README.")
    sys.exit(4)

with open("./auth.txt") as auth:
    token = auth.read().strip()

base = "https://pixels.pythondiscord.com"
print(Fore.LIGHTBLUE_EX + "[RATELIMIT] " + Fore.LIGHTGREEN_EX + "Syncing ratelimit...")
handle_sane_ratelimit(
    requests.head(base + "/set_pixel", headers={"Authorization": "Bearer " + token})
)
canvas_size_response = requests.get(base + "/get_size").json()
canvas_width = int(canvas_size_response["width"])
canvas_height = int(canvas_size_response["height"])

print(f"{Fore.MAGENTA}[CANVAS] {Fore.WHITE}(W:H) {canvas_width}:{canvas_height}")

start_x, start_y = map(int, input("Cursor will start at: ").split(","))
end_x, end_y = map(int, input("Cursor will end at: ").split(","))

assert end_x > start_x, "end x is smaller than start x."
assert end_y >= start_y, "end y is smaller than start y"
image_width = (end_x - start_x) - 1
image_height = (end_y - start_y) - 1

image_path = input("Image path (provide URL for download): ")
if image_path.startswith("http"):
    image_response = requests.get(image_path)
    assert (
        image_response.headers["Content-Type"] == "image/png"
    ), "Incorrect image type."
    with open("image_download.png", "wb+") as download:
        download.write(image_response.content)
        image_bytes = image_response.content
else:
    with open(image_path, "rb") as file:
        image_bytes = file.read()

pilImage: Image = Image.open(BytesIO(image_bytes))
pilImage: Image = pilImage.convert("RGB")
pilImage: Image = pilImage.resize((image_width, image_height))
pilImage: Image = resizeOption(pilImage, canvas_width, canvas_height)

pixels_array = getPixels(pilImage)
pixels_map: Dict[Tuple[int, int], str] = {}
for e in pixels_array:
    r, g, b, *_ = e[2]
    if "dev" in sys.argv:
        print(
            Fore.RED
            + "[DEBUG] "
            + Fore.LIGHTBLACK_EX
            + "R: {} G: {} B: {} _: {}".format(r, g, b, _)
        )
    _hex = ""
    _hex += hex(r).replace("0x", "").zfill(2)
    _hex += hex(g).replace("0x", "").zfill(2)
    _hex += hex(b).replace("0x", "").zfill(2)
    pixels_map[(e[0], e[1])] = _hex
    if "dev" in sys.argv:
        print(Fore.RED + "[DEBUG] X: {} Y: {} HEX: {}".format(e[0], e[1], _hex))


def paint():
    canvas_cursor: List[int] = [start_x - 1, start_y - 1]
    image_cursor: List[int] = [-1, -1]
    painted = 0

    print(
        Fore.YELLOW + "[CURSOR] ",
        Fore.CYAN + "Beginning paint. It will likely finish at",
        (
            datetime.datetime.now() + datetime.timedelta(seconds=len(pixels_array))
        ).strftime("%X"),
    )
    for x, y in pixels_map.keys():
        # noinspection PyTypeChecker
        try:
            colour = pixels_map[(x, y)]
        except KeyError:
            if "dev" in sys.argv:
                print(
                    Fore.RED
                    + "[DEBUG] {} is not in colour map? Going to continue.".format(
                        str(image_cursor)
                    )
                )
                continue
        print(
            Fore.YELLOW
            + "[CURSOR] "
            + Fore.LIGHTYELLOW_EX
            + "Painting {} #{}.".format((x, y), colour)
        )
        set_pixel(x+start_x, y+start_y, colour=colour, token=token, base=base)
        painted += 1
        pct = round((painted / len(pixels_array)) * 100, 2)
        print(
            Fore.YELLOW
            + "[CURSOR] "
            + Fore.LIGHTGREEN_EX
            + "Painted {} #{}. {}% done.".format((x, y), colour, pct)
        )
    print(Fore.YELLOW + "[CURSOR] ", Fore.LIGHTGREEN_EX + "Done!")


if "loop" in sys.argv:
    if len(sys.argv) >= 3 and sys.argv[2].isdigit():
        count = int(sys.argv[2])
        print("looping {} times".format(count))
        for i in range(count):
            paint()
    else:
        print("looping \N{infinity} times")
        while True:
            paint()
else:
    print("Running one-shot")
    paint()
