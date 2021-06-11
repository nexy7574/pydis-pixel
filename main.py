#!/usr/bin/env python3
import datetime
import os
import sys
import traceback

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
        status = api.set_pixel(*cursor, colour=colour)
        painted += 1
        pct = round((painted / len(pixels_array)) * 100, 2)
        if status is True and not args.quiet:
            print(Fore.YELLOW + "[CURSOR] " + Fore.LIGHTGREEN_EX + "Painted {} #{}. {}% done.".format(cursor,
                                                                                                      colour, pct))
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
