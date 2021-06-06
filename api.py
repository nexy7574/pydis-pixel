import json
import sys
import time

import requests

from kool import Fore


def getPixels(img):
    pixels = []
    for x in range(img.width):
        for y in range(img.height):
            pixels.append((x, y, img.getpixel((x, y))))
    return pixels


def set_pixel(*at: int, colour: str, token: str, base: str = "https://pixels.pythondiscord.com"):
    if "dev" in sys.argv:
        print(f"{Fore.RED}[DEBUG] {Fore.LIGHTBLACK_EX}Args for setting pixel: at={at} colour={colour} token={{no}}")
    try:
        response = requests.post(
            base + "/set_pixel",
            json={"x": at[0], "y": at[1], "rgb": colour},
            headers={"Authorization": "Bearer " + token},
        )
    except (requests.HTTPError, requests.HTTPError, requests.RequestException):
        print(f"{Fore.YELLOW}[WARNING] {Fore.WHITE}Exception while setting a pixel. Retrying.")
        return set_pixel(*at, colour=colour, token=token)
    handle_sane_ratelimit(response)
    if response.status_code == 429:
        # try again
        print(f"{Fore.CYAN}[API] {Fore.LIGHTRED_EX}set_pixel call previously failed due to ratelimit. Retrying {at}.")
        set_pixel(*at, colour=colour, token=token)
        return
    if response.status_code != 200:
        if response.headers.get("content-type", "null") == "application/json":
            print(
                f"{Fore.RED}[ERROR] {Fore.LIGHTWHITE_EX}Non-200 pixel set code. "
                f"Data:\n{json.dumps(response.json(), indent=2)}"
            )
        else:
            print(f"{Fore.RED}[ERROR] {Fore.LIGHTWHITE_EX}Non-200 pixel set code. " f"Data:\n{response.text}")


def handle_sane_ratelimit(res):
    remaining = int(res.headers.get("requests-remaining", 0))
    if res.status_code == 429:
        reset = float(res.headers["cooldown-reset"])
        print(
            f"{Fore.CYAN}[RATELIMITER] {Fore.LIGHTRED_EX}On hard cooldown for",
            reset,
            "seconds.",
            file=sys.stderr,
        )
        time.sleep(reset)
    else:
        if remaining == 0:
            try:
                reset = float(res.headers["requests-reset"])
            except KeyError:
                print(
                    f"{Fore.RED}[DEBUG][RATELIMITER] {Fore.LIGHTBLACK_EX} Some whacky shit is going on with"
                    f" headers, here's a list of them:\n" + "\n".join(f"{k}: {v}" for k, v in res.headers.items()),
                    "\nJust going to pretend it doesn't exist.",
                )
                return
            print(
                f"{Fore.CYAN}[RATELIMITER] {Fore.LIGHTYELLOW_EX}On soft cooldown for",
                reset,
                "seconds.",
            )
            time.sleep(reset)
