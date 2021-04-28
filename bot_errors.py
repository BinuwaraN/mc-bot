class InvalidRefreshRate(Exception):
    def __init__(self, refresh_rate):
        super().__init__(f"Refresh rate must be 30 or higher. You have it set to {refresh_rate}.")

class NotOnServerError(Exception):
    """You need to run this command on 24CC"""

class NoPermissionError(Exception):
    pass

class FuckyWucky:
    """You made one."""

class EmptryString(Exception):
    """Empty string provided"""