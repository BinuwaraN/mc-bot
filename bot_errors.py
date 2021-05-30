class InvalidRefreshRate(Exception):
    def __init__(self, refresh_rate):
        super().__init__(
            f"Refresh rate must be 30 or higher. You have it set to {refresh_rate}.")