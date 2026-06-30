from abc import ABC, abstractmethod

class Basenotifierclass(ABC):
    @abstractmethod
    def notifier(self):
        pass