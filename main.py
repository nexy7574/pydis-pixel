import httpx
from lib.cli import arguments
from lib import http
from lib.console import console
from rich.prompt import Prompt
from pathlib import Path

client = http.Client()
image_data: bytes = b""

if arguments.image is None:
    image_uri = Prompt.ask(
        "Image URI (path or HTTP url)",
        console=console
    )
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


async def main():
    if arguments.end_pos == "auto":
        pass
