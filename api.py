import json
import sys
import time
from typing import List, Tuple

import requests

from kool import Fore


def get_pixels(img) -> List[Tuple[int, int, Tuple[int, int, int]]]:
    """
    Fetches an array of [x, y, (r, g, b)] in the image, with x, y being the x,y co-ords and rgb being the rgb values.

    :param img: the PIL.Image
    :return: List[Tuple[int, int, Tuple[int, int, int]]]
    """
    pixels = []
    for x in range(img.width):
        for y in range(img.height):
            pixels.append((x, y, img.getpixel((x, y))))
    return pixels


def set_pixel(*at: int, colour: str, token: str, base: str = "https://pixels.pythondiscord.com"):
    """
    Handles all the fuss setting pixels in places.

    :param at: A pair of x, y co-ords to set the pixel at
    :param colour: The hex value to set
    :param token: Your API token
    :param base: The base API URL. You should change this in main.py if needs be, not here.
    :return: None
    """
    if "dev" in sys.argv:
        print(f"{Fore.RED}[DEBUG] {Fore.LIGHTBLACK_EX}Args for setting pixel: at={at} colour={colour} token={{no}}")
    try:
        response = requests.post(
            base + "/set_pixel",
            json={"x": at[0], "y": at[1], "rgb": colour},
            headers={"Authorization": "Bearer " + token},
        )
    except (requests.HTTPError, requests.HTTPError, requests.RequestException):
        print(f"{Fore.YELLOW}[WARNING] {Fore.WHITE}Exception while setting a pixel. Retrying in 5 seconds.")
        time.sleep(5)
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
            print(f"{Fore.RED}[ERROR] {Fore.LIGHTWHITE_EX}Non-200 pixel set code. Data:\n{response.text}")


def handle_sane_ratelimit(res):
    """
    Handles ratelimits in a way that prevents getting 429s, but also handles actual 429s.

    Soft cooldown is when the function detects that the next request would be ratelimited
    Hard cooldown is when the response status was 429, indicating a ratelimit.

    :param res: The response object
    :return: Nothing
    """
    remaining = int(res.headers.get("requests-remaining", 0))
    if res.status_code == 429:
        reset = float(res.headers["cooldown-reset"])
        print(
            f"{Fore.CYAN}[RATELIMITER] {Fore.LIGHTRED_EX}On hard cooldown for",
            reset,
            "seconds.\nThis only really tends to happen if you're running multiple instances.\n"
            "If you're unsure why you've got a 429, check:\n"
            "1. You haven't restarted the program while it was on a cooldown (it'll reset the handler)\n"
            "2. You aren't running the program elsewhere\n"
            "3. Your token hasn't been leaked. If you believe it has, reset it ASAP.",
            file=sys.stderr,
        )
        time.sleep(reset)
    else:
        if remaining == 0:
            try:
                reset = float(res.headers["requests-reset"])
            except KeyError:
                headers_joined = "\n".join(f"{k}: {v}" for k, v in res.headers.items())
                print(
                    f"{Fore.RED}[DEBUG][RATELIMITER] {Fore.LIGHTBLACK_EX} A lack of ratelimit headers were sent:\n"
                    + headers_joined + "\nGoing to ignore ratelimit handling for this request, and pray we haven't"
                                       " stumbled upon a hard limit."
                )
                return
            print(
                f"{Fore.CYAN}[RATELIMITER] {Fore.LIGHTYELLOW_EX}On soft cooldown for",
                reset,
                "seconds.",
            )
            time.sleep(reset)
