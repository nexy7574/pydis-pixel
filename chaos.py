import os
import sys

from lib import api, arguments
from random import randint
width = ...
height = ...

if arguments.end_x:
    width = arguments.end_x
if arguments.end_y:
    height = arguments.end_y
if width is ... or height is ...:
    width, height = api.get_size()
colour = os.getenv("COLOUR", "RANDOMISE")

iteration = 0
while True:
    iteration += 1
    if not iteration % 300:
        width, height = api.get_size()
    x = randint(0, width)
    y = randint(0, height)
    if colour.upper() == "RANDOMISE":
        col = randint(0x0, 0xFFFFFF)
    else:
        col = int(colour, 16)
    h = hex(col)[2:]
    print(f"[CURSOR] Setting ({x}, {y}) to #{h}")
    api.set_pixel(x, y, h)
