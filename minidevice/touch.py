from abc import ABC, abstractclassmethod


class Touch(ABC):
    @abstractclassmethod
    def click(self, x: int, y: int, duration: int):
        """点击"""

    @abstractclassmethod
    def swipe(self, points: list, duration: int):
        """滑动"""
