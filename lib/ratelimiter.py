import datetime
import asyncio
from httpx import Headers
from .console import console


async def simple_handle(headers: Headers, path: str = None) -> None:
    """
    Simple ratelimit call that checks to see if there are any requests remaining (in the requests-remaining header)
    and then sleeps until requests-reset is reached.
    """
    requests_remaining: float = float(headers.get("requests-remaining", "0"))
    cooldown_resets_at: float = float(headers.get("cooldown-reset", "-1"))
    bucket_resets_at: float = float(headers.get("requests-reset", "-1"))
    console.log(
        "[debug][Ratelimiter] (for {!r}) Requests remaining: {!s} | cooldown resets at: {!s}s | "
        "bucket resets at: {!s}s".format(
            path or "/unknown-path", requests_remaining, cooldown_resets_at, bucket_resets_at
        )
    )
    if cooldown_resets_at > 0:
        # We have hit a 429 hard ratelimit.
        # Sleep until the cooldown resets.
        console.log(f"[info][Ratelimiter] Sleeping {cooldown_resets_at!s}s until 429 resets on {path!r}.")
        await asyncio.sleep(cooldown_resets_at)

    else:
        if bucket_resets_at > 0 and requests_remaining == 0:
            # We have hit a soft ratelimit and don't have to wait as long as a 429.
            console.log(f"[info][Ratelimiter] Sleeping {bucket_resets_at!s}s until bucket resets on {path!r}.")
            await asyncio.sleep(bucket_resets_at)
        else:
            console.log(
                f"[debug][Ratelimiter] Bucket resets at is {bucket_resets_at!s}s, and requests remaining "
                f"is {requests_remaining!s} - nothing to do on {path!r}!."
            )
        # else, we have nothing to do!


# MAYBE: add a class because everyone loves classes and class-based code makes me look smart
