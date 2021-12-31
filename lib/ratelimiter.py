import datetime
import asyncio
from httpx import Headers


async def simple_handle(headers: Headers) -> None:
    """
    Simple ratelimit call that checks to see if there are any requests remaining (in the requests-remaining header)
    and then sleeps until requests-reset is reached.
    """
    requests_remaining: int = int(headers.get("requests-remaining", "0"))
    cooldown_resets_at: int = int(headers.get("cooldown-reset", "-1"))
    bucket_resets_at: int = int(headers.get("requests-reset", "-1"))
    if cooldown_resets_at:
        # We have hit a 429 hard ratelimit.
        # Sleep until the cooldown resets.
        await asyncio.sleep(cooldown_resets_at)

    else:
        if bucket_resets_at > 0 and requests_remaining == 0:
            # We have hit a soft ratelimit and don't have to wait as long as a 429.
            await asyncio.sleep(bucket_resets_at)
        # else, we have nothing to do!


# MAYBE: add a class because everyone loves classes and class-based code makes me look smart
