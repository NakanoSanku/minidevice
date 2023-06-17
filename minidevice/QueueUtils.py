import threading
from collections import deque
from queue import Queue
from time import monotonic as time


class LoopQueue:
    def __init__(self, maxsize: int = 10):
        self.maxsize = maxsize
        self._queue = Queue(maxsize)

    def put(self, item):
        size = self._queue.qsize()
        if size >= self.maxsize:
            for _ in range(size - self.maxsize + 1):
                self._queue.get()
        # 添加新数据
        self._queue.put(item)

    def get(self):
        return self._queue.get()

    def size(self) -> int:
        return self._queue.qsize()

    def empty(self) -> bool:
        return self._queue.empty()


class Empty(Exception):
    pass


class PipeQueue:
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._queue = deque(maxlen=maxsize)
        self._mutex = threading.Lock()
        self._not_empty = threading.Condition(self._mutex)

    def put(self, item):
        with self._mutex:
            self._put(item)
            self._not_empty.notify()

    def get(self, block=True, timeout=None):
        with self._not_empty:
            if not block:
                if not self._size():
                    raise Empty
            elif timeout is None:
                while not self._size():
                    self._not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                end_time = time() + timeout
                while not self.size():
                    remaining = end_time - time()
                    if remaining <= 0.0:
                        raise Empty
                    self._not_empty.wait(remaining)
            item = self._get()
            return item

    def size(self):
        with self._mutex:
            return self._size()

    def empty(self):
        with self._mutex:
            return not self._size()

    def _put(self, item):
        self._queue.append(item)

    def _get(self):
        return self._queue.popleft()

    def _size(self):
        return len(self._queue)
