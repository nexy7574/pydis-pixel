import json
import sys
import time
from typing import List, Tuple
from datetime import datetime, timedelta

import requests
from requests.structures import CaseInsensitiveDict

from .kool import Fore


class Pixel(list):
    """
    Describes a pixel

    Attributes:
        x: int - the X (horizontal) co-ordinate
        y: int - the Y (vertical) co-ordinate
        rgb: str - the hexadecimal value
        hex: str - the hexadecimal value
    """

    def __init__(self, x: int, y: int, rgb: str):
        self.x = x
        self.y = y
        self.rgb = rgb
        self.hex = rgb
        super().__init__((x, y, rgb))


class Api:
    """
    OOP API Container
    """

    def __init__(self, base: str = "https://pixels.pythondiscord.com"):
        self.session = requests.session()
        self.base = base

    def __del__(self):
        self.session.close()

    def _request(self, uri: str, method: str = "GET", **kwargs):
        response = self.session.request(method, uri, **kwargs)
        if response.status_code in range(500, 600):  # server error:
            raise RuntimeError(f"Pixels server appears to be down ({response.status_code}).")
        self.wait_out_ratelimit(response.headers)
        return response.status_code, response.json()

    def get_pixel(self, x: int, y: int) -> Pixel:
        """
        Fetches a pixel from the remote canvas.

        :param x: The X (horizontal) co-ordinate of the target pixel
        :param y: X but Y
        :return: Pixel - The Found pixel.
        :raises: ValueError - the co-ordinates were out of range
        """
        response = self.session.get(self.base + "/get_pixel", params={"x": x, "y": y})
        if response.status_code == 422:
            # The only cause for this is an axis is out of range.
            raise ValueError("One or more axis were out of range.")
        self.wait_out_ratelimit(response.headers)
        if response.status_code not in [200, 429]:  # 429 is handled by the above.
            response.raise_for_status()
        _json = response.json()
        return Pixel(*_json.values())

    def set_pixel(self, x: int, y: int, colour: str):
        """
        Sets a pixel on the canvas

        :param x: The X (horizontal) co-ordinate of the target pixel
        :param y: You can figure this one out
        :param colour: The hexadecimal colour
        :return:
        """
        response = self._request(
            "/set_pixel",
            "POST",
            json={"x": x, "y": y, "rgb": colour}
        )

    @staticmethod
    def wait_out_ratelimit(headers: CaseInsensitiveDict):
        remaining = int(headers.get("requests-remaining", 0))
        soft_cooldown = float(headers.get("requests-reset", 300.0))
        hard_cooldown = float(headers.get("cooldown-reset", 0.0))
        if not hard_cooldown:
            if remaining == 0:  # Soft cooldown
                expire = datetime.now() + timedelta(seconds=soft_cooldown)
                print(
                    f"{Fore.CYAN}[RATELIMITER] {Fore.LIGHTYELLOW_EX}On {Fore.LIGHTGREEN_EX}soft cooldown"
                    f"{Fore.LIGHTYELLOW_EX} for {Fore.LIGHTCYAN_EX}{soft_cooldown} seconds{Fore.LIGHTYELLOW_EX} "
                    f"(until {Fore.LIGHTCYAN_EX}{expire.strftime('%X')}{Fore.LIGHTYELLOW_EX})."
                )
        else:
            if hard_cooldown == float("inf"):
                raise ValueError("Hard cooldown is way too long (to be precise, it's infinite)")
            expire = datetime.now() + timedelta(seconds=hard_cooldown)
            print(
                f"{Fore.CYAN}[RATELIMITER] {Fore.LIGHTYELLOW_EX}On {Fore.RED}hard cooldown"
                f"{Fore.LIGHTYELLOW_EX} for {Fore.LIGHTCYAN_EX}{hard_cooldown} seconds{Fore.LIGHTYELLOW_EX} "
                f"(until {Fore.LIGHTCYAN_EX}{expire.strftime('%X')}{Fore.LIGHTYELLOW_EX})."
            )
            time.sleep(hard_cooldown)

    def sync_ratelimit(self, endpoint: str = "set_pixel"):
        """
        Simply sends a HEAD request and waits for the timeout.

        :return:
        """
        response = self._request("/"+endpoint.lower(), "HEAD")
        return handle_sane_ratelimit(response)


def get_pixels(img) -> List[Tuple[int, int, Tuple[int, int, int]]]:
    """
    Fetches an array of [x, y, (r, g, b)] in the image, with x, y being the x,y co-ords and rgb being the rgb values.

    :param img: the PIL.Image
    :return: List[Tuple[int, int, Tuple[int, int, int]]]
    """
    pixels = []
    for y in range(img.height):
        for x in range(img.width):
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
        preflight_response = requests.get(
            base + "/get_pixel", params={"x": at[0], "y": at[1]}, headers={"Authorization": "Bearer " + token}
        )
        handle_sane_ratelimit(preflight_response)
        if preflight_response.json()["rgb"] == colour:
            print(f"{Fore.CYAN}[API] {at} was already set. ignoring.")
            return 300
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
        return set_pixel(*at, colour=colour, token=token)
    if response.status_code != 200:
        if response.headers.get("content-type", "null") == "application/json":
            print(
                f"{Fore.RED}[ERROR] {Fore.LIGHTWHITE_EX}Non-200 pixel set code. "
                f"Data:\n{json.dumps(response.json(), indent=2)}"
            )
            return -1
        else:
            print(f"{Fore.RED}[ERROR] {Fore.LIGHTWHITE_EX}Non-200 pixel set code. Data:\n{response.text}")
            return -1
    return 200


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
                    + headers_joined
                    + "\nGoing to ignore ratelimit handling for this request, and pray we haven't"
                    " stumbled upon a hard limit."
                )
                return
            print(
                f"{Fore.CYAN}[RATELIMITER] {Fore.LIGHTYELLOW_EX}On soft cooldown for",
                reset,
                "seconds.",
            )
            time.sleep(reset)
