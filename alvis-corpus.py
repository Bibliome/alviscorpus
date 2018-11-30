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
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def init():
        logger = logging.getLogger(LOGGER_ROOT)
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(logging.Formatter(LoggerConfig.MESSAGE_FORMAT, LoggerConfig.DATE_FORMAT))
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
        filehandler.setFormatter(logging.Formatter(LoggerConfig.MESSAGE_FORMAT, LoggerConfig.DATE_FORMAT))
        result.addHandler(filehandler)
        result.setLevel(logging.DEBUG)
        return result
    

class Document:
    def __init__(self):
        self.doi = None
        self.data = defaultdict(dict)

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

    
class Event:
    def __init__(self, ftor, args, kwargs):
        self.ftor = ftor
        self.args = args
        self.kwargs = kwargs

    def process(self):
        self.ftor(*self.args, **self.kwargs)

        
class Provider(threading.Thread):
    _singleton = None
    
    def __init__(self):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        self.queue = Queue()
        self.closed = False
        self.logger = LoggerConfig.logger(self.__class__.__name__)
        
    def run(self):
        try:
            while True:
                try:
                    event = self.queue.get_nowait()
                except Empty:
                    if self.closed:
                        self.logger.info('closing queue')
                        break
                    continue
                delay = self.delay()
                if delay > 0:
                    self.logger.warning('delay %ss' % str(delay))
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
        cls._singleton.queue.put(Event(ftor, args, kwargs))

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
            self.logger.error('past reset')
            return 0
        return int(ceil(self.reset - time.time()))

    def update(self, headers):
        self.remain -= 1

def log(msg):
    RemainResetTest._singleton.logger.info(msg)

Config.read('alvis-corpus.rc')
LoggerConfig.init()
for i in range(10):
    RemainResetTest.register(log, 'task: %d' % i)
RemainResetTest.close()

