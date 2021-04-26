class InvalidRefreshRate(Exception):
    def __init__(self, refresh_rate):
        super().__init__(f"Refresh rate must be 30 or higher. You have it set to {refresh_rate}.")

class BotError(Exception):
    """Base class for exceptions in this module."""
    pass

class NotOnServerError(BotError):
    """You need to run this command on 24CC"""


class FuckyWucky:
    """You made one."""

class EmptryString(BotError):
    """Empty string provided"""