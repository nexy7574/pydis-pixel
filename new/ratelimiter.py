from datetime import datetime, timedelta


class Bucket:
    def __init__(self, *, hits: int, cooldown: float):
        self.max_hits = hits
        self.hits = 0
        self.cooldown = cooldown
        self.expires = datetime.min

    @property
    def ratelimited(self) -> bool:
        r"""
        Boolean indicating if the current route is ratelimited.
        :return: True if a request would become ratelimited, otherwise False.
        """
        return self.hits >= self.max_hits and datetime.utcnow() <= self.expires

    @property
    def retry_after(self) -> float:
        r"""
        Floating point number indicating how long, in seconds, until the current ratelimit has expired.

        .. Note::
            This function ALWAYS returns a float. This means ``0.0`` will be returned if there's no ratelimit active.

        :return: How long (in seconds) until the current ratelimit is over.
        """
        if not self.expires:
            return 0.0
        return max((self.expires - datetime.utcnow()).total_seconds(), 0.0)

    def sync_from_ratelimit(self, reset: float):
        r"""
        Syncs the internal ratelimit clock to that of a 429 response.
        """
        self.hits = self.max_hits
        self.expires = datetime.utcnow() + timedelta(seconds=reset)

    def add_hit(self):
        r"""Handles adding a hit to the route and dealing with the datetime-y stuff"""
        self.hits += 1
        if self.expires is None or self.expires <= datetime.utcnow():
            self.expires = datetime.utcnow() + timedelta(seconds=self.cooldown)


ratelimits = {}
