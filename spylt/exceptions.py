class PointerNotFoundError(Exception):
    """Raised when a Svelte file does not point to a Python file"""


class TypesNotDefinedError(Exception):
    "Raised when types are not defined on Python functions"


class NoRoutesDefinedError(Exception):
    "Raised when routes are not defined for the backend API"
