from typing import List

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class SkabenTopics:

    RGB = "rgb"
    SCL = "scl"
    PWR = "pwr"
    BOX = "box"
    LOCK = "lock"
    TERMINAL = "terminal"

    @property
    def smart(self) -> List[str]:
        return [self.LOCK, self.TERMINAL]

    @property
    def simple(self) -> List[str]:
        return [
            self.BOX,
            self.RGB,
            self.SCL,
            self.PWR,
        ]

    @property
    def scale_topic(self) -> str:
        return self.SCL


@lru_cache
def get_topics():
    return SkabenTopics()
