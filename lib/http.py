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
    def __init__(self, x: int, y: int, rgb: str):
        self.x = x
        self.y = y
        self.colour = rgb

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y

    def __repr__(self):
        return "Pixel(pos={0.position}, colour=0x{0.colour})".format(self)

    def __iter__(self):
        return iter(self.position)

    @property
    def payload(self):
        return {"x": self.x, "y": self.y, "rgb": self.colour.replace("0x", "").replace("#", "")}


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

    @property
    def valid_auth(self) -> bool:
        now = datetime.now()
        if self.auth["access_token"] is None or self.auth["expires_at"] <= now:
            return False
        return True

    @property
    def auth_expires_soon(self) -> bool:
        """Returns true if the access token expires within the next 5 minutes."""
        now = datetime.now()
        return self.auth["expires_at"] - now <= timedelta(minutes=5)

    async def _request(self, method: str, uri: str, data: dict = None, *, ensure_200: bool = False) -> httpx.Response:
        if self.valid_auth is False or self.auth_expires_soon is True:
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
            console.log(fr"[warn]\[warning] Ratelimit exceeded for {built.url.path!r} - waiting...")
            await simple_handle(response.headers, f"{built.method} {built.url.path!s}")
            console.log(fr"[debug]\[debug] Ratelimit for {built.url.path!r} has been reset.")
            return await self._request(method, uri, data, ensure_200=ensure_200)
        else:
            await simple_handle(response.headers, f"{built.method!s} {built.url.path!s}")
            # await self.clear_all_ratelimits()
            if ensure_200:
                response.raise_for_status()

        return response

    async def authenticate(self, refresh_token: str) -> None:
        """
        Gets an access token from the pixels server.

        :param refresh_token: The refresh token to use for authentication.
        """
        console.log(fr"[debug]\[debug] POST {self._http.base_url!s}/authenticate...")
        response = await self._http.post("/authenticate", json={"refresh_token": refresh_token})
        console.log(fr"[debug]\[debug] POST {self._http.base_url!s}/authenticate -> {response.status_code!s}")
        response.raise_for_status()
        data = response.json()
        self.auth["access_token"] = data["access_token"]
        self.auth["refresh_token"] = data["refresh_token"]  # future-proofing.
        self.auth["expires_at"] = datetime.now() + timedelta(seconds=data["expires_in"])
        console.log(fr"[debug]\[debug] Access token: {self.auth['access_token']!r}")

    async def clear_all_ratelimits(self) -> None:
        """Simple function to wait for all ratelimits to expire."""
        tasks = []
        endpoints = ["/canvas_pixels", "/get_pixel", "/put_pixel"]
        for endpoint in endpoints:
            response = await self._http.head(endpoint)
            tasks.append(simple_handle(response.headers, f"HEAD {endpoint!s}"))

        console.log(r"[info]\[info] Waiting for all ratelimits to expire...")
        await asyncio.wait(tasks, timeout=None)
        console.log(r"[info]\[info] Ratelimits expired.")

    async def get_size(self) -> Tuple[int, int]:
        console.log(fr"[debug]\[debug] GET {self._http.base_url!s}/canvas_size...")
        response = await self._request("GET", "/canvas/size")
        console.log(fr"[debug]\[debug] GET {self._http.base_url!s}/canvas_size -> {response.status_code!s}")
        response.raise_for_status()
        data = response.json()
        return data["width"], data["height"]

    async def get_pixel(self, x: int, y: int) -> Pixel:
        """
        Fetches a pixel
        """
        response = await self._request("GET", f"/canvas/pixel?x={x}&y={y}")
        return Pixel(**response.json())

    async def put_pixel(self, pixel: Pixel) -> None:
        current = await self.get_pixel(pixel.x, pixel.y)
        if current.colour != pixel.colour:
            await self.blind_put_pixel(pixel)

    async def blind_put_pixel(self, pixel: Pixel) -> None:
        """
        The same as Client.put_pixel, except it checks to see if the pixel actually needs setting first.

        This should only be used if you're writing a subclass and are avoiding every ratelimit down to the T
        (since the regular method makes two requests, compared to one.)
        """
        await self._request("PUT", "/canvas/pixel", data=pixel.payload)

    async def get_all_pixels(self) -> bytes:
        response = await self._request("GET", "/canvas/pixels")
        return response.content

    async def get_canvas(self, resize_to: Tuple[int, int] = None) -> Image:
        data = await self.get_all_pixels()
        x, y = await self.get_size()
        image = Image.frombytes("RGB", (x, y), data)
        if resize_to:
            image = image.resize(resize_to, Image.NEAREST)
        return image
