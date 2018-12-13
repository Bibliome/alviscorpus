import threading
from queue import Queue, Empty
import sys
import time
from math import ceil
import logging
from os import makedirs
import os.path
from configparser import ConfigParser
from collections import defaultdict
from urllib.parse import quote as urlquote
import json
import uuid


LOGGER_ROOT = 'alviscorpus'
CONFIG_GLOBAL = 'global'
CONFIG_LOGGING = 'logging'
CONFIG_OUTDIR = 'outdir'
CONFIG_DOCS = 'documents'


Config = ConfigParser(default_section=CONFIG_GLOBAL, interpolation=None)
Config[CONFIG_GLOBAL][CONFIG_OUTDIR] = '.'
Config.add_section(CONFIG_LOGGING)
Config.add_section(CONFIG_DOCS)


class LoggerConfig:
    MESSAGE_FORMAT = '[%(asctime)s][%(levelname)-8s][%(name)s] %(message)s'

    @staticmethod
    def init():
        logger = logging.getLogger(LOGGER_ROOT)
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(logging.Formatter(LoggerConfig.MESSAGE_FORMAT))
        logger.addHandler(handler)

    @staticmethod
    def logger(name):
        result = logging.getLogger('%s.%s' % (LOGGER_ROOT, name))
        dirpath = Config[CONFIG_LOGGING][CONFIG_OUTDIR]
        if not os.path.exists(dirpath):
            makedirs(dirpath)
        path = '%s/%s.log' % (dirpath, name)
        filehandler = logging.FileHandler(path, 'w')
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(logging.Formatter(LoggerConfig.MESSAGE_FORMAT))
        result.addHandler(filehandler)
        result.setLevel(logging.DEBUG)
        return result
    

class Document:
    def __init__(self):
        self.local_id = str(uuid.uuid4())
        self.doi = None
        self.data = defaultdict(dict)
        self.finished_steps = []

    def __str__(self):
        if self.doi is None:
            return self.local_id
        return self.doi

    def safe_doi(self):
        if self.doi is None:
            raise Exception()
        return urlquote(self.doi)
    
    def get_dir(self):
        if self.doi is None:
            raise Exception()
        outdir = Config[CONFIG_DOCS][CONFIG_OUTDIR]
        return os.path.join(outdir, self.safe_doi())

    def get_filename(self, ext):
        basename = '%s.%s' % (self.safe_doi(), ext)
        return os.path.join(self.get_dir(), basename)
    
    def dump_metadata(self):
        outfile = self.get_filename('md.json')
        with open(outfile) as f:
            json.dump(self.data)


class Step:
    REGISTRY = {}
    
    def __init__(self, name, provider):
        if name in Step.REGISTRY:
            raise Exception()
        Step.REGISTRY[name] = self
        self.name = name
        self.logger = LoggerConfig.logger(name)
        self.provider = provider

    def enqueue(self, doc, arg=None):
        self.provider.register(self, doc, arg)
        
    def process(self, doc, arg=None):
        raise NotImplemented()

    @staticmethod
    def get(name):
        if name not in Step.REGISTRY:
            raise Exception()
        return Step.REGISTRY[name]


class Provider(threading.Thread):
    _singleton = None
    
    def __init__(self):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        self.queue = Queue()
        self.closed = False
	#self.logger = LoggerConfig.logger(self.__class__.__name__)

    def run(self):
        try:
            while True:
                try:
                    step, doc, arg = self.queue.get_nowait()
                except Empty:
                    if self.closed:
                        #self.logger.info('closing queue')
                        break
                    continue
                delay = self.delay()
                if delay > 0:
                    step.logger.warning('delay %ss' % str(delay))
                time.sleep(delay)
                try:
                    next_name, next_arg = step.process(doc, arg)
                except Exception as e:
                    step.logger.warning('exception while processing %s with %s' % (doc, step.name), exc_info=True)
                    continue
                doc.finished_steps.append(step.name)
                if next_name is not None:
                    next_step = Step.get(next_name)
                    next_step.enqueue(doc, next_arg)
        finally:
            pass
        
    def delay(self):
        raise NotImplemented()

    @classmethod
    def register(cls, step, doc, arg=None):
        if cls._singleton is None:
            cls._singleton = cls()
            cls._singleton.start()
        cls._singleton.queue.put((step, doc, arg))

    @classmethod
    def close(cls):
        if cls._singleton is not None:
            cls._singleton.closed = True


class RemainResetTest(Provider):
    def __init__(self, remain=2, reset=time.time()+2):
        Provider.__init__(self)
        self.remain = remain
        self.reset = reset

    def delay(self):
        if self.remain is None:
            return 0
        if self.remain > 0:
            return 0
        now = time.time()
        if now > self.reset:
            #self.logger.error('past reset')
            return 0
        return int(ceil(self.reset - time.time()))

    @classmethod
    def set_remain(cls, remain):
        cls._singleton.remain = remain
        
class TestStep1(Step):
    def __init__(self):
        Step.__init__(self, 'step1', RemainResetTest)

    def process(self, doc, arg):
        self.logger.info('doing: %s' % doc)
        self.provider.set_remain(-1)
        return 'step2', 'foo'

class TestStep2(Step):
    def __init__(self):
        Step.__init__(self, 'step2', RemainResetTest)

    def process(self, doc, arg):
        self.logger.info('redoing: %s (arg is %s; path is %s)' % (doc, arg, doc.finished_steps))
        raise Exception()
        return None, None

Config.read('alvis-corpus.rc')
LoggerConfig.init()
step1 = TestStep1()
step2 = TestStep2()
for i in range(10):
    step1.enqueue(Document())
RemainResetTest.close()

