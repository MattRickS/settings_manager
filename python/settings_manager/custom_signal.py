import weakref


class Signal(object):
    def __init__(self, *args):
        self.args = args
        self._connections = list()

        # Map instances to signals - weakref so the instances aren't kept alive
        self.__signals = weakref.WeakKeyDictionary()

    def __call__(self, *args, **kwargs):
        self.emit(*args)

    def __get__(self, instance, owner):
        if instance is not None:
            return self.__signals.setdefault(instance, Signal())
        return self

    def connect(self, func):
        self._connections.append(func)

    def disconnect(self, func):
        self._connections.remove(func)

    def emit(self, *args):
        for func in self._connections:
            func(*args)
