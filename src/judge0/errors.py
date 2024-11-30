"""Library specific errors."""


class PreviewClientLimitError(RuntimeError):
    """Limited usage of a preview client exceeded."""


class ClientResolutionError(RuntimeError):
    """Failed resolution of an unspecified client."""
