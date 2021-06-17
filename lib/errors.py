class BasePixelsException(Exception):
    """Base class for pixels-related exceptions. Nothing special."""


class APIException(BasePixelsException):
    """Error indicating there was an error from the pixels server."""
    def __init__(self, status: int, detail: str = "No Detail", *, message: str = None):
        self.status = status
        self.detail = detail
        self.message = message
        super().__init__(self.status, self.detail, self.message)

    def __str__(self):
        ret = f"Response from pixels server was not okay: {self.status} - {self.detail}"
        if self.message:
            ret += " | " + self.message
        return ret


class AxisOutOfRange(APIException):
    """Error representing when the X or Y co-ordinate was more than the canvas' max."""


class APIOffline(APIException):
    """Raised whenever a 5xx is encountered"""


class Unauthorized(APIException):
    """You forgot to provide a token, or it was invalid."""


class Forbidden(Unauthorized):
    """For when you're banned from the API :pensive:"""
