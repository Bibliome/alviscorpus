import threading
import queue
import time
import itertools

import alviscorpus.config as config
import alviscorpus.status as status
import alviscorpus.step as step
import alviscorpus.document as document


class Provider(threading.Thread):
    _singleton = None
    
    def __init__(self):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        self.queue = queue.Queue()
        self.closed = False
        self.lock = threading.Lock()

    def run(self):
        config.logger.info('queue started: %s' % self.__class__.__name__)
        while True:
            try:
                thestep, doc, arg = self.queue.get_nowait()
            except queue.Empty:
                if self.closed:
                    config.logger.info('queue closed: %s' % self.__class__.__name__)
                    break
                time.sleep(0)
                continue
            delay = self.delay()
            if delay > 0:
                thestep.logger.warning('delay %ss' % str(delay))
            time.sleep(delay)
            try:
              doc.set_status(thestep.name, status.STARTED)
              next_name, next_arg = thestep.process(doc, arg)
              doc.set_status(thestep.name, status.FINISHED)
            except Exception as e:
                doc.set_status(thestep.name, status.ERROR)
                thestep.logger.warning('exception while processing %s with %s' % (doc, thestep.name), exc_info=True)
                end_report_step = step.get(step.END)
                end_report_step.enqueue(doc, None)
                continue
            if next_name is None:
                doc.release()
                if document.all_released():
                    step.close_providers()
            else:
                next_step = step.get(next_name)
                next_step.enqueue(doc, next_arg)
        
    def delay(self):
        raise NotImplemented()

    @classmethod
    def init(cls):
        if cls._singleton is None:
            cls._singleton = cls()
            cls._singleton.start()

    @classmethod
    def register(cls, step, doc, arg=None):
        if cls._singleton is None:
            raise Exception('queue not started: %s' % cls.__name__)
        cls._singleton.queue.put((step, doc, arg))

    @classmethod
    def close(cls):
        if cls._singleton is not None:
            with cls._singleton.lock:
                cls._singleton.closed = True


class ConstantDelayProvider(Provider):
    def __init__(self, delay_value=0):
        Provider.__init__(self)
        self.delay_value = delay_value

    def delay(self):
        return self.delay_value


_pool = None
def pool():
    global _pool
    if _pool is None:
        ctor = lambda self: ConstantDelayProvider.__init__(self, 0)
        classes = [type('PoolProvider%02d' % i, (ConstantDelayProvider,), { '__init__': ctor }) for i in range(int(config.val(config.OPT_THREAD_POOL)))]
        _pool = itertools.cycle(classes)
    return next(_pool)



class LimitIntervalProvider(Provider):
    def __init__(self, limit=None, interval=None):
        Provider.__init__(self)
        self.limit = limit
        self.interval = interval
        self.last = None

    def delay(self):
        if self.limit is None or self.interval is None or self.last is None:
            self.last = time.time()
            return 0
        d = float(self.interval) / self.limit
        r = self.last + d - time.time()
        if r < 0:
            r = 0
        self.last = time.time() + r
        return r
