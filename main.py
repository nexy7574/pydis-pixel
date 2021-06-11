#!/usr/bin/env python3
import datetime
import sys
import traceback
from copy import copy
from signal import SIGUSR1, signal, SIGUSR2

import requests

from lib import Fore, arguments as args, render, api

base = args.base
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

pilImage, pixels_map, pixels_array = render(image_width, image_height)


def paint():
    """
    Handles painting on the canvas.

    This is the main runtime, only in a function to allow for easier looping.
    """
    painted = 0
    cursor = (0, 0)

    def signal_handler(num, frame):
        if num == SIGUSR1:
            pct = round((painted / len(pixels_array)) * 100, 2)
            print(f"{Fore.MAGENTA}[SIGUSR1]{Fore.WHITE} {painted}/{len(pixels_array)}, {pct}% complete.")
        elif num == SIGUSR2:
            nonlocal cursor
            local_cursor = copy(cursor)
            image = api.get_pixels()
            image = image.convert("RGBA")
            # _draw = Draw(image)
            # _draw.line((cursor[0], 0, cursor[0], end_y), fill="blue")
            # _draw.line((0, cursor[1], 0, end_x), fill="orange")
            for _x in range(image.width):
                for _y in range(image.height):
                    if _x == local_cursor[0]:
                        image.putpixel((_x, _y), (255, 0, 0, 0.2))
                    if _y == local_cursor[1]:
                        image.putpixel((_x, _y), (0, 0, 255, 0.2))
            image = image.resize((1920, 1080))
            image.save("./cursor.png")

    print(
        Fore.YELLOW + "[CURSOR] ",
        Fore.CYAN + "Beginning paint. It will likely finish at",
        (datetime.datetime.now() + datetime.timedelta(seconds=len(pixels_array))).strftime("%X"),
    )
    signal(SIGUSR1, signal_handler)
    signal(SIGUSR2, signal_handler)
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
        status = api.set_pixel(*cursor, colour=colour)
        painted += 1
        pct = round((painted / len(pixels_array)) * 100, 2)
        if status is True and args.quiet is False:
            print(Fore.YELLOW + "[CURSOR] " + Fore.LIGHTGREEN_EX + "Painted {} #{}. {}% done.".format(cursor,
                                                                                                      colour, pct))
        if status is None and args.quiet is False:
            print(Fore.YELLOW + "[CURSOR] " + Fore.LIGHTCYAN_EX + "{} Already painted. {}% done.".format(
                cursor, pct
            ))
    print(Fore.YELLOW + "[CURSOR] ", Fore.LIGHTGREEN_EX + "Done!")


if args.loop is not None:
    if isinstance(args.loop, bool):
        print("Running \N{infinity} times.")
        while True:
            try:
                paint()
            except Exception:
                print("Exception in iteration ...:", file=sys.stderr)
                traceback.print_exc()
    if isinstance(args.loop, int):
        print("Running", args.loop, "times.")
        for i in range(args.loop):
            try:
                paint()
            except Exception:
                print(f"Exception in iteration {i}:", file=sys.stderr)
                traceback.print_exc()
else:
    print("Running once.")
    paint()
