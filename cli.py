from argparse import ArgumentParser
from pathlib import Path


def path_like(i: str):
    if i.startswith("http"):
        # I is a URL
        return i
    p = Path(i).resolve()
    assert p.exists(), "Invalid path"
    return p


def loop_validator(v: str):
    if v.isdigit():
        return int(v)
    elif v.lower() in ["infinity", "infinite", "forever", "24/7"]:
        return True
    elif v.lower() == "once":
        return
    else:
        raise ValueError(v, "is not a recognised loop count. Try \"once\", a number, or \"forever\".")


parser = ArgumentParser()
parser.add_argument(
    "--verbose",
    "--dev",
    action="store_true",
    default=False,
    help="Toggles verbose output on/off. Useful for debugging."
)
parser.add_argument(
    "--loop",
    "-L",
    action="store",
    required=False,
    default=None,
    type=loop_validator,
    help="How may times to loop self. If you don't pass an argument, this will loop forever."
)
parser.add_argument(
    "--quiet",
    "-Q",
    action="store_true",
    default=False,
    help="If enabled, will only show pixels that've been painted (minus warnings and errors)"
)
parser.add_argument(
    "--image",
    "-I",
    action="store",
    default=None,
    type=path_like,
    help="A path to an image. If not provided, will be interactively collected."
)
parser.add_argument(
    "--cursor-start-x",
    "-X",
    action="store",
    default=None,
    type=int,
    help="Where the X co-ordinate of the cursor should start",
    dest="start_x"
)
parser.add_argument(
    "--cursor-end-x",
    "-H",
    action="store",
    default=None,
    type=int,
    help="Where the X co-ordinate of the cursor should end",
    dest="end_x"
)
parser.add_argument(
    "--cursor-start-y",
    "-Y",
    action="store",
    default=None,
    type=int,
    help="Where the Y co-ordinate of the cursor should start",
    dest="start_y"
)
parser.add_argument(
    "--cursor-end-y",
    "-V",
    action="store",
    default=None,
    type=int,
    help="Where the Y co-ordinate of the cursor should end",
    dest="end_y"
)
parser.add_argument(
    "--auth",
    "--token",
    "-A",
    action="store",
    default=None,
    help="Your API token from https://pixels.pythondiscord.com/show_token"
)
parser.add_argument(
    "--base",
    "--api-url",
    action="store",
    default="https://pixels.pythondiscord.com",
    help="The base API url."
)

arguments = parser.parse_args()

if __name__ == '__main__':
    print(arguments)
