from src.core.clock import Clock


class Timeline(Clock):
    def __init__(self):
        super().__init__("monotonic")
