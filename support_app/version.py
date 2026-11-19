"""Single source of truth for the Macrosoft Support version."""

__version__ = "1.0.0"


def version_tuple() -> tuple[int, int, int, int]:
    """Return the version as the four-part tuple Windows version info needs."""
    parts = [int(part) for part in __version__.split(".")]
    if len(parts) > 4:
        raise ValueError(f"Unsupported version: {__version__}")
    parts += [0] * (4 - len(parts))
    return parts[0], parts[1], parts[2], parts[3]


def version_string() -> str:
    """Return the version as a Windows ``major.minor.patch.revision`` string."""
    return ".".join(str(part) for part in version_tuple())
