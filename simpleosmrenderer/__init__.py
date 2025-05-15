"""Top-level package for SimpleOSMRenderer."""
__all__ = ["renderer"]
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("SimpleOSMRenderer")
except PackageNotFoundError:  # local checkout
    __version__ = "0.1.0"
