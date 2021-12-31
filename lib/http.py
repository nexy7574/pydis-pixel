import asyncio
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional, Union

import httpx
from PIL import Image

from .cli import arguments, __version__
from .console import console
from .ratelimiter import simple_handle
from . import exceptions


class Pixel:
    def __init__(self, x: int, y: int, colour: str):
        self.x = x
        self.y = y
        self.colour = int(colour, base=16)

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y

    def __repr__(self):
        return "Pixel(pos={0.position}, colour=0x{0.colour:x})".format(self)

    def __iter__(self):
        return iter(self.position)

    @property
    def payload(self):
        return {"x": self.x, "y": self.y, "rgb": hex(self.colour)[2:]}


class Client:
    def __init__(self):
        self._http = httpx.AsyncClient(
            base_url=arguments.base,
            follow_redirects=True,
            trust_env=True,
            headers={
                "User-Agent": f"EEKIM10/pydis-pixel (https://github.com/EEKIM10/pydis-pixel, v{__version__}),"
                f" python-httpx/{httpx.__version__}"
            },
        )
        self.auth: Dict[str, Optional[Union[str, datetime]]] = {
            "access_token": None,
            "refresh_token": None,
            "expires_at": None,
        }

    def valid_auth(self) -> bool:
        now = datetime.now()
        if self.auth["access_token"] is None or self.auth["expires_at"] <= now:
            return False
        return True

    async def _request(self, method: str, uri: str, data: dict = None, *, ensure_200: bool = False) -> httpx.Response:
        if self.valid_auth() is False:
            assert self.auth["refresh_token"] is not None, "No refresh token"
            await self.authenticate(self.auth["refresh_token"])

        built = self._http.build_request(
            method, uri, json=data, headers={"Authorization": "Bearer " + self.auth["access_token"]}
        )
        console.log(rf"[debug]\[debug] {built.method!s} {built.url.path!s}...")
        response = await self._http.send(built)
        console.log(rf"[debug]\[debug] {built.method!s} {built.url.path!s} -> {response.status_code!s}")

        if response.status_code == 401:
            raise exceptions.Unauthorised(message=response.json())

        if response.status_code == 422:
            raise exceptions.InvalidPixel(message=response.json())

        if response.status_code == 429:
            console.log(fr"[warn]\[Warning] Ratelimit exceeded for {built.url.path!r} - waiting...")
            await simple_handle(response.headers)
            console.log(fr"[debug]\[Debug] Ratelimit for {built.url.path!r} has been reset.")

        if ensure_200:
            response.raise_for_status()
        return response

    async def authenticate(self, refresh_token: str) -> None:
        """
        Gets an access token from the pixels server.

        :param refresh_token: The refresh token to use for authentication.
        """
        response = await self._http.post("/authenticate", json={"refresh_token": refresh_token})
        response.raise_for_status()
        data = response.json()
        self.auth["access_token"] = data["access_token"]
        self.auth["refresh_token"] = data["refresh_token"]
        self.auth["expires_at"] = datetime.now() + timedelta(seconds=data["expires_in"])

    async def clear_all_ratelimits(self) -> None:
        """Simple function to wait for all ratelimits to expire."""
        tasks = []
        endpoints = ["/canvas_pixels", "/get_pixel", "/put_pixel"]
        for endpoint in endpoints:
            response = await self._http.head(endpoint)
            tasks.append(simple_handle(response.headers))

        console.log(r"[info]\[info] Waiting for all ratelimits to expire...")
        await asyncio.gather(*tasks, return_exceptions=True)
        console.log(r"[info]\[info] Ratelimits expired.")

    async def get_size(self) -> Tuple[int, int]:
        response = await self._request("GET", "/size")
        data = response.json()
        return data["width"], data["height"]

    async def get_pixel(self, x: int, y: int) -> Pixel:
        """
        Fetches a pixel
        """
        response = await self._request("GET", f"/canvas/pixel?x={x}&y={y}")
        return Pixel(**response.json())

    async def put_pixel(self, pixel: Pixel) -> None:
        await self._request("PUT", "/canvas/pixel", data=pixel.payload)

    async def get_all_pixels(self) -> bytes:
        response = await self._request("GET", "/canvas/pixels")
        return response.content

    async def get_canvas(self, resize_to: Tuple[int, int] = None) -> Image:
        data = await self.get_all_pixels()
        x, y = await self.get_size()
        image = Image.frombytes(
            "RGB",
            (x, y),
            data
        )
        if resize_to:
            image = image.resize(resize_to, Image.NEAREST)
        return image
