from typing import Protocol
from pygame import Surface


class VisualizerProtocol(Protocol):
    screen: Surface
