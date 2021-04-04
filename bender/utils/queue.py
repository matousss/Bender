class Queue(object):
    def __init__(self, size: int = -1):
        if size != -1 and size < 1:
            raise ValueError("Size parameter must be -1 for unlimited or greater than 1")

        self._list = list()
        self.QUEUE_SIZE = size

        pass

    def append(self, value):
        if len(self._list) is self.QUEUE_SIZE:
            raise self.QueueFull("Queue is full")

        self._list.append(value)
        pass

    def insert(self, index: int, value):
        self._list.insert(index, value)
        pass

    def pop(self, index: int = 0):
        if len(self._list) == 0:
            raise self.QueueEmpty("Queue is empty")

        return self._list.pop(index)

    def get(self, index = 0):
        try:
            return self._list[index]
        except Exception as e:
            raise e
        pass

    def remove(self, index: int = 0):
        try:
            self._list.remove(self._list[index])
        except Exception as e:
            raise e

    def max_size(self) -> int:
        return self.QUEUE_SIZE

    def __str__(self):
        return str(self._list)
    pass

    def __len__(self):
        return len(self._list)

    class QueueEmpty(Exception):
        def __init__(self, message: str = ""):
            self.message = message
            super().__init__(message)
            pass

    class QueueFull(Exception):
        def __init__(self, message: str = ""):
            self.message = message
            super().__init__(message)
            pass


q = Queue()
q.append("jo")
q.append("ne")
q.append("traktor")
print(str(q))
print(q.remove(1))
print(str(q))

q.insert(1, "auto")
print(str(q))
print("sdads "+q.get(-2))
print(q.pop())
print(str(q))
print(len(q))