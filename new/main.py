import datetime
import sys
from typing import Dict, Tuple, List
import requests
from PIL import Image
from io import BytesIO
from api import getPixels, resizeOption, set_pixel, handle_sane_ratelimit
from kool import Fore

with open("../auth.txt") as auth:
    token = auth.read().strip()

base = "https://pixels.pythondiscord.com"
print(Fore.LIGHTBLUE_EX + "[RATELIMIT] " + Fore.LIGHTGREEN_EX + "Syncing ratelimit...")
handle_sane_ratelimit(requests.head(base + "/get_pixels", headers={"Authorization": "Bearer " + token}))
canvas_size_response = requests.get(base + "/get_size").json()
canvas_width = int(canvas_size_response["width"])
canvas_height = int(canvas_size_response["height"])

print(f"{Fore.MAGENTA}[CANVAS] {Fore.WHITE}(W:H) {canvas_width}:{canvas_height}")

start_x, start_y = map(int, input("Cursor will start at: ").split(","))
end_x, end_y = map(int, input("Cursor will end at: ").split(","))

assert end_x > start_x, "end x is smaller than start x."
assert end_y >= start_y, "end y is smaller than start y"
image_width = end_x - start_x
image_height = end_y - start_y

image_path = input("Image path (provide URL for download): ")
if image_path.startswith("http"):
    image_response = requests.get(image_path)
    assert image_response.headers["Content-Type"] == "image/png", "Incorrect image type."
    with open("image_download.png", "wb+") as download:
        download.write(image_response.content)
        image_bytes = image_response.content
else:
    with open(image_path, "rb") as file:
        image_bytes = file.read()

pilImage = Image.open(BytesIO(image_bytes))
pilImage = pilImage.convert("RGB")
pilImage = pilImage.resize((image_width, image_width))


pilImage = resizeOption(pilImage, canvas_width, canvas_height)
pixels_array = getPixels(pilImage)
pixels_map: Dict[Tuple[int, int], str] = {}
for e in pixels_array:
    r, g, b, *_ = e[2]
    if "dev" in sys.argv:
        print(Fore.RED + "[DEBUG] " + Fore.LIGHTBLACK_EX + "R: {} G: {} B: {} _: {}".format(r, g, b, _))
    _hex = ""
    _hex += hex(r).replace("0x", "").zfill(2)
    _hex += hex(g).replace("0x", "").zfill(2)
    _hex += hex(b).replace("0x", "").zfill(2)
    pixels_map[(e[0], e[1])] = _hex
    if "dev" in sys.argv:
        print(Fore.RED + "[DEBUG] " + Fore.LIGHTBLACK_EX + "hex:", _hex)

canvas_cursor: List[int] = [start_x - 1, start_y - 1]
image_cursor: List[int] = [-1, -1]
painted = 0

print(Fore.YELLOW + "[CURSOR] ", Fore.CYAN + "Beginning paint. It will likely finish at",
      (datetime.datetime.now() + datetime.timedelta(seconds=len(pixels_array))).strftime("%X"))
for y in range(pilImage.height):
    canvas_cursor[1] += 1
    image_cursor[1] += 1
    for x in range(pilImage.width):
        canvas_cursor[0] += 1
        image_cursor[0] += 1
        # noinspection PyTypeChecker
        try:
            colour = pixels_map[tuple(image_cursor)]
        except KeyError:
            if "dev" in sys.argv:
                print(
                    Fore.RED+"[DEBUG] {} is not in colour map? Going to continue.".format(str(image_cursor))
                )
        print(Fore.YELLOW + "[CURSOR] " + Fore.LIGHTYELLOW_EX + " Painting {} #{}.".format(str(canvas_cursor), colour))
        set_pixel(*canvas_cursor, colour=colour, token=token)
        painted += 1
        pct = round((painted / len(pixels_array)) * 100, 2)
        print(
            Fore.YELLOW
            + "[CURSOR] "
            + Fore.LIGHTGREEN_EX
            + "Painted {} #{}. {}% done.".format(str(canvas_cursor), colour, pct)
        )
print(Fore.YELLOW + "[CURSOR] ", Fore.LIGHTGREEN_EX + "Done!")
