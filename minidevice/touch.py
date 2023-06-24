from abc import ABC, abstractclassmethod


class Touch(ABC):
    @abstractclassmethod
    def click(self, x: int, y: int, duration: int = 100):
        """
        click 点击

        Args:
            x (int): 横坐标
            y (int): 纵坐标
            duration (int, optional): 持续时间. Defaults to 100.
        """

    @abstractclassmethod
    def swipe(self, points: list, duration: int = 300):
        """
        swipe 滑动

        Args:
            points (list): [(x,y),(x,y),(x,y)] 坐标列表
            duration (int): 持续时间. Defaults to 300.
        """
