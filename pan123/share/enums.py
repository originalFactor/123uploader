__all__ = ["TrafficSwitchEnum"]

from enum import IntEnum


class TrafficSwitchEnum(IntEnum):
    CLOSE = 1
    ONLY_VISITORS = 2
    ONLY_OVERLOAD = 3
    ALL = 4
