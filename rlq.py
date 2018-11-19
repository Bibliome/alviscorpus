import threading
from Queue import Queue


class Event:
    def __init__(self, ftor, args, kwargs):
        self.ftor = ftor
        self.args = args
        self.kwargs = kwargs

    def process(self):
        self.ftor(*self.args, **self.kwargs)

    
class RLQThread(threading.Thread):
    _singleton = None
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue()

    def register(self, ftor, args, kwargs):
        self.queue.put(Event(ftor, args, kwargs))
        
    def run(self):
        while True:
            datum = self.queue.get()
            delay = self.limiter.delay()
            sleep(delay)
            ret = self.process(datum)
            self.limiter.update(ret)

    def delay(self):
        raise NotImplemented()
    
    def update(self, headers):
        raise NotImplemented()

    @classmethod
    def register(cls, ftor, datum):
        if cls._singleton is None:
            cls._singleton = cls()
            cls._singleton.start()
        cls._singleton.register(datum)


