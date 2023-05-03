"""
A collection of exceptions that can be raised by the API.
"""


class Conflict(Exception):
    """When a resource already exists or operation can be performed
    because of the inconsistent state of the DB or App."""
    message = "Conflict"

    def __init__(self, message: str = None):
        if message:
            self.message = message

    def __str__(self):
        return self.message


class NotFound(Exception):
    """When a resource is not found."""
    message: str = "Not Found"

    def __init__(self, message: str = None):
        if message:
            self.message = message

    def __str__(self):
        return self.message
