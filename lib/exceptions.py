class HTTPException(Exception):
    """
    Base class for all HTTP exceptions.
    """

    def __init__(self, status_code: int, *args, **kwargs):
        super().__init__(*args, kwargs)
        self.status = status_code
        self.message = kwargs.pop("message", None)

    def __repr__(self):
        return f"<HTTPException {self.status} detail={self.message!s}>"

    def __str__(self):
        return str(self.message)

    def __int__(self):
        return self.status


class InvalidPixel(HTTPException):
    """
    An error raised when an HTTP 422 error is encountered.

    This means that a pixel was placed outside the canvas
    """

    def __init__(self, *args, **kwargs):
        super().__init__(422, *args, **kwargs)


class Unauthorised(HTTPException):
    """
    An error raised when an HTTP 401 error is encountered.

    This means that the user is not authorised to access the resource. Make sure you called `Client.authorise()` first.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(401, *args, **kwargs)
