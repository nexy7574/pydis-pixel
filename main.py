import asyncio

import httpx
from lib.cli import arguments
from lib import http
from lib.console import console
from lib.image import convert_bytes, get_pixels
from lib.cursor import Cursor
from rich.prompt import Prompt
from pathlib import Path

client = http.Client()
image_data: bytes = b""

if arguments.image is None:
    image_uri = Prompt.ask("Image URI (path or HTTP url)", console=console)
else:
    image_uri = arguments.image
path = Path(image_uri)
if not path.exists():
    try:
        response = httpx.get(image_uri)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        console.print(e)
        exit(1)
    except httpx.UnsupportedProtocol:
        console.print(f"Unsupported protocol: {image_uri}")
        exit(1)
    else:
        image_data = response.content
else:
    image_data = path.read_bytes()


if arguments.token is None:
    arguments.token = Prompt.ask(f"[link={arguments.base}/authorize]Pixels API Refresh Token")


async def main():
    try:
        await client.authenticate(arguments.token)
    except httpx.HTTPStatusError as err:
        if err.response.status_code == 403:
            # Invalid refresh token
            console.log(f"Invalid refresh token. Please go to "
                        f"{err.request.url.scheme}://{err.request.url.netloc.decode()}/authorize")
        else:
            console.log("Got error code %r when authenticating." % err.response.reason_phrase)
        exit(1)
    await client.clear_all_ratelimits()

    image = convert_bytes(image_data)
    canvas_size = await client.get_size()
    if arguments.end_pos == "auto":
        if image.size > canvas_size:
            image = image.resize(canvas_size)
        arguments.end_pos = image.size

    if canvas_size < arguments.end_pos:
        console.log(
            f"[warn][Warning] Canvas is only {'x'.join(map(str, canvas_size))}px, but image "
            f"is {'x'.join(map(str, arguments.end_pos))}px."
        )
    console.log(
        f"[info]\\[info] Image Size: {image.size}\nCanvas Size: {canvas_size}\nStart Position: {arguments.start_pos}\n"
        f"End Position: {arguments.end_pos}"
    )
    cursor = Cursor(client, get_pixels(image), arguments.end_pos)
    await client.clear_all_ratelimits()
    await cursor.paint_all()


async def runtime():
    # noinspection PyProtectedMember
    async with client._http:
        await main()


if __name__ == "__main__":
    asyncio.run(runtime())
