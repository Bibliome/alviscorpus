import threading
from Queue import Queue
import sys
import time
from math import ceil

class Event:
    def __init__(self, ftor, args, kwargs):
        self.ftor = ftor
        self.args = args
        self.kwargs = kwargs

    def process(self):
        self.ftor(*self.args, **self.kwargs)


EndQueue = object()
        
    
class RLQThread(threading.Thread):
    _singleton = None
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue()

    def _register(self, ftor, args, kwargs):
        self.queue.put(Event(ftor, args, kwargs))

    def _close(self):
        self.queue.put(EndQueue)
        
    def run(self):
        try:
            while True:
                event = self.queue.get()
                if event is EndQueue:
                    log(sys.stderr, 'closing queue')
                    break
                delay = self.delay()
                log(sys.stderr, 'delay = ' + str(delay))
                time.sleep(delay)
                ret = event.process()
                self.update(ret)
        finally:
            pass
        
    def delay(self):
        raise NotImplemented()
    
    def update(self, headers):
        raise NotImplemented()

    @classmethod
    def register(cls, ftor, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = cls()
            cls._singleton.start()
        cls._singleton._register(ftor, args, kwargs)

    @classmethod
    def close(cls):
        if cls._singleton is not None:
            cls._singleton._close()
        

class RemainResetTest(RLQThread):
    def __init__(self, remain=0, reset=time.time()+2):
        RLQThread.__init__(self)
        self.remain = remain
        self.reset = reset

    def delay(self):
        if self.remain is None:
            return 0
        if self.remain > 0:
            return 0
        now = time.time()
        if now > self.reset:
            log(sys.stderr, 'past reset')
            return 0
        log(sys.stderr, 'hafta wait')
        return int(ceil(self.reset - time.time()))

    def update(self, headers):
        pass


def log(f, msg):
    f.write('[%s] %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg))
    f.flush()
    
for i in range(10):
    RemainResetTest.register(log, sys.stdout, str(i))
RemainResetTest.close()

