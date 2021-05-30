import sys
import time
from io import BytesIO
from typing import List, Tuple
from datetime import datetime

import requests
from PIL import Image

import loader

log = open("./log.txt", "a+")
log.write(f"[{datetime.utcnow().strftime('%x')} | INFO] Logger created.\n")

try:
    with open("./auth.txt") as file:
        token = file.read().strip()
except FileNotFoundError:
    print("You don't appear to have any auth tokens. Please create a file called auth.txt and put your token in there.")
    sys.exit(4)

headers = {"User-Agent": "Notice me senpai uwu (https://yourapps.cyou)", "Authorization": "Bearer " + token}

base = "https://pixels.pythondiscord.com"


class Pixel:
    def __init__(self, x: int, y: int, rgb, cw, ch) -> None:
        self.x = x
        self.y = y
        self.rgb = int(rgb, base=16)
        self.hex = hex(self.rgb)
        self.cw = cw
        self.ch = ch

    def __repr__(self):
        return f"Pixel(x={self.x} y={self.y} hex={self.hex.replace('0x', '#')})"

    @property
    def json(self):
        return {"x": (self.cw // 4) + self.x, "y": (self.ch // 2) + self.y, "rgb": self.hex[2:]}


def handle_sane_ratelimit(res):
    log.write(str(res.status_code) + " " + str(res.headers) + "\n")
    if res.status_code == 429:
        log.write(
            f"[{datetime.utcnow().strftime('%x')} | WARN] Ratelimited for {res.headers['cooldown-reset']} seconds.\n"
        )
        print("On hard cooldown for", res.headers["cooldown-reset"], "seconds.", file=sys.stderr)
        time.sleep(float(res.headers["cooldown-reset"]))
    else:
        if int(res.headers["requests-remaining"]) == 0 or int(res.headers["requests-limit"]) == 0:
            log.write(
                f"[{datetime.utcnow().strftime('%x')} | WARN] Soft ratelimited for {res.headers['requests-reset']} secs.\n"
            )
            time.sleep(float(res.headers["requests-reset"]))


def getPixels(image: Image) -> List[Pixel]:
    canvas_width, canvas_height = get_canvas_size()
    results = []
    if image.mode != "RGB":
        image = image.convert("RGB")
    for x in range(image.width):
        for y in range(image.height):
            r, g, b = image.getpixel((x, y))
            _hex = hex(r) + hex(g) + hex(b)
            _hex = _hex.replace("0x", "")
            results.append(Pixel(x, y, _hex, canvas_width, canvas_height))
    return results


def get_pixel(x: int, y: int):
    response = requests.get(base + "/get_pixel", params={"x": x, "y": y}, headers=headers)
    handle_sane_ratelimit(response)
    response.raise_for_status()
    data = response.json()
    return Pixel(*data.values(), *get_canvas_size())  # note: THIS WILL RATELIMIT AT SOME POINT


def get_canvas_size():
    response = requests.get(base + "/get_size")
    data = response.json()
    return int(data["width"]), int(data["height"])


def set_pixel(pixel: Pixel, check: bool = False):
    if check:
        p = get_pixel(pixel.x, pixel.y)
        if p.hex.lower() == pixel.hex.lower():
            log.write(f"[{datetime.utcnow().strftime('%x')} | INFO] Skipping pixel {repr(pixel)} (already set).")
    response = requests.post(base + "/set_pixel", json=pixel.json, headers=headers)
    if response.status_code == 422:
        return
    handle_sane_ratelimit(response)
    if response.status_code == 429:
        set_pixel(pixel)
    log.write(f"[{datetime.utcnow().strftime('%x')} | INFO] {response.json()['message']}\n")


def main():
    while True:
        url = input("URI of image: ")
        if url.startswith("./"):
            with open(url, "rb") as _old_image:
                _image_data = _old_image.read()
        else:
            print("GETting URL...")
            response = requests.get(url)
            if response.headers["Content-Type"] != "image/png":
                print("URL Did not return image/png.")
                continue
            _image_data = response.content
        img = Image.open(BytesIO(_image_data))
        if input("Would you like to... shrink this image? ").lower().startswith("y"):
            new_value = input("Width, Height: ")
            if new_value.split(", "):
                t = map(int, new_value.split(", "))
            else:
                t = (int(new_value), int(new_value))
            img = img.resize(t, Image.BILINEAR)
        print("Loaded image successfully, loading pixels...")
        pixels = getPixels(img)
        print(f"Loaded {len(pixels)} pixels.")
        for n, pixel in enumerate(pixels):
            print(loader.calculateBar(n, len(pixels), disable_safety=True), end="\r")
            set_pixel(pixel, check=True)
            time.sleep(60.0)
        print(loader.calculateBar(len(pixels), len(pixels), disable_safety=True))
        print("Done!")


try:
    main()
except KeyboardInterrupt:
    print("\nOkay, bye!")
finally:
    log.close()
