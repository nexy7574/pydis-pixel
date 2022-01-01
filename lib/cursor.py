import asyncio

import httpx

from .http import Client, Pixel
from .cli import arguments
from .image import PIXEL_DATA, rgba_to_hex
from .console import console
from typing import Tuple


def get_pixel(x: int, y: int, data: PIXEL_DATA) -> Tuple[int, int, Tuple[int, int, int, int]]:
    for _x, _y, colour_info in data:
        # This is HORRIBLY inefficient, especially for larger(?) images.
        # Perhaps look into using a dictionary instead?
        if _x == x and _y == y:
            return _x, _y, colour_info


class Cursor:
    def __init__(self, client: Client, image_data: PIXEL_DATA, end_pos: tuple):
        self.client = client
        self.image_data = image_data
        self.start_pos = arguments.start_pos
        self.end_pos = end_pos
        self.cursor_loc = self.start_pos

    @property
    def pixels(self):
        result = []
        y_range = self.end_pos[1] - self.start_pos[1]
        x_range = self.end_pos[0] - self.start_pos[0]
        for y in range(y_range):
            for x in range(x_range):
                result.append((x, y))
        return result

    async def paint_all(self):
        for pixel_location in self.pixels:
            console.log(fr"[debug][Cursor] Location is now {pixel_location}")
            pixel_data = get_pixel(*pixel_location, data=self.image_data)[2]
            colour = rgba_to_hex(*pixel_data, rgb_only=True)
            console.log(fr"[debug][Cursor] Pixel data is now: {pixel_data} (#{colour})")
            pixel = Pixel(*pixel_location, rgb=colour)
            console.log(fr"[info][Cursor] Painting {pixel_location} [#{colour}]#{colour}[/]...")
            for i in range(10):
                i += 1
                try:
                    await self.client.put_pixel(pixel)
                    break
                except httpx.ConnectError:
                    console.log(fr"[error][Cursor] Could not connect to server. Retrying in {i/2} seconds...")
                    await asyncio.sleep(i/2)
            console.log(fr"[info][Cursor] Painted [#{colour}]{pixel_location}[/].")
