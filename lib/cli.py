import re
import os
from argparse import ArgumentParser
from typing import Tuple
from dotenv import load_dotenv


__version__ = "0.0.1a"


load_dotenv(verbose=True)


def validate_position_input(value: str) -> Tuple[int, int]:
    position = re.match(r"\d([:,-])\d", value)
    assert position is not None, "Invalid position. Please provide in the format 'x:y' or 'x,y'."
    x, y = map(int, position.group().split(position.group(1)))
    return x, y


parser = ArgumentParser(allow_abbrev=True)
parser.add_argument("--no-colour", action="store_true", help="Disables coloured output.")
parser.add_argument(
    "--base",
    action="store",
    help="The base URL for the pixels API. Defaults to http://localhost:8000",
    default="http://localhost:8000",
)
parser.add_argument(
    "-q",
    "--q",
    action="count",
    dest="quiet",
    help="Controls how verbose the output is. 0 is Debug, 1 is Info, 2 is Warning, 3 is Error, 4 is Critical.",
)
parser.add_argument("start_pos", action="store", type=validate_position_input, default=(0, 0), required=False)
parser.add_argument(
    "end_pos",
    action="store",
    type=lambda val: val.lower().strip() == "auto" or validate_position_input(val),
    default="auto",
    required=False,
)
parser.add_argument(
    "--image",
    action="store",
    help="The image to use for the pixels.",
    default=os.getenv("IMAGE_PATH"),
)

arguments = parser.parse_args()
