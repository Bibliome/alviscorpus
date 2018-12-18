import threading
from queue import Queue, Empty
import sys
import time
from math import ceil
import logging
from os import makedirs
import os.path
from configparser import ConfigParser
from collections import defaultdict, OrderedDict
from urllib.parse import quote as urlquote
import json
import uuid
from enum import Enum


class Config(ConfigParser):
    _singleton = None
    LOGGER_ROOT = 'alviscorpus'
    SECTION_GLOBAL = 'global'
    SECTION_LOGGING = 'logging'
    SECTION_DOCS = 'documents'
    OPT_OUTDIR = 'outdir'
    OPT_REPORT_FILENAME = 'report'
    MESSAGE_FORMAT = '[%(asctime)s][%(levelname)-8s][%(name)s] %(message)s'
    LOGGER = None
    
    def __init__(self):
        ConfigParser.__init__(self, default_section=Config.SECTION_GLOBAL, interpolation=None)
        self[Config.SECTION_GLOBAL][Config.OPT_OUTDIR] = '.'
        self[Config.SECTION_GLOBAL][Config.OPT_REPORT_FILENAME] = 'report.txt'
        self.add_section(Config.SECTION_LOGGING)
        self.add_section(Config.SECTION_DOCS)

    @staticmethod
    def load(filename):
        return Config._singleton.read(filename)
    
    @staticmethod
    def val(arg1, arg2=None):
        if arg2 is None:
            section = Config.SECTION_GLOBAL
            opt = arg1
        else:
            section = arg1
            opt = arg2
        return Config._singleton[section][opt]

    @staticmethod
    def init_logger():
        logger = logging.getLogger(Config.LOGGER_ROOT)
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(logging.Formatter(Config.MESSAGE_FORMAT))
        logger.addHandler(handler)
        Config.LOGGER = Config.get_logger('alviscorpus')

    @staticmethod
    def get_logger(name):
        result = logging.getLogger('%s.%s' % (Config.LOGGER_ROOT, name))
        dirpath = Config.val(Config.SECTION_LOGGING, Config.OPT_OUTDIR)
        if not os.path.exists(dirpath):
            makedirs(dirpath)
        path = os.path.join(dirpath, name + '.log')
        filehandler = logging.FileHandler(path, 'w')
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(logging.Formatter(Config.MESSAGE_FORMAT))
        result.addHandler(filehandler)
        result.setLevel(logging.DEBUG)
        return result
Config._singleton = Config()


class Status(Enum):
    QUEUED = 'queued'
    STARTED = 'started'
    FINISHED = 'finished'
    ERROR = 'error'

    def __str__(self):
        return self.value

    
class Document:
    count = 0
    lock = threading.Lock()
    
    def __init__(self):
        self.local_id = str(uuid.uuid4())
        self.doi = None
        self.data = defaultdict(dict)
        self.status = OrderedDict()
        with Document.lock:
            Document.count += 1

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
        outdir = Config.get(Config.SECTION_DOCS, Config.OPT_OUTDIR)
        return os.path.join(outdir, self.safe_doi())

    def get_filename(self, ext):
        basename = '%s.%s' % (self.safe_doi(), ext)
        return os.path.join(self.get_dir(), basename)
    
    def dump_metadata(self):
        outfile = self.get_filename('md.json')
        with open(outfile) as f:
            json.dump(self.data)

    def set_status(self, step, status):
        self.status[step] = status


class Step:
    REGISTRY = {}
    
    def __init__(self, name, provider):
        if name in Step.REGISTRY:
            raise Exception()
        Step.REGISTRY[name] = self
        self.name = name
        self.logger = Config.get_logger(name)
        self.provider = provider

    def enqueue(self, doc, arg=None):
        self.provider.register(self, doc, arg)
        doc.set_status(self.name, Status.QUEUED)
        
    def process(self, doc, arg=None):
        raise NotImplemented()

    @staticmethod
    def get(name):
        if name not in Step.REGISTRY:
            raise Exception('unknown step: %s' % name)
        return Step.REGISTRY[name]

    @staticmethod
    def init_providers():
        for step in Step.REGISTRY.values():
            step.provider.init()

    @staticmethod
    def close_providers():
        for step in Step.REGISTRY.values():
            step.provider.close()


class Provider(threading.Thread):
    _singleton = None
    
    def __init__(self):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        self.queue = Queue()
        self.closed = False
        self.lock = threading.Lock()

    def run(self):
        Config.LOGGER.info('queue started: %s' % self.__class__.__name__)
        while True:
            try:
                step, doc, arg = self.queue.get_nowait()
            except Empty:
                if self.closed:
                    Config.LOGGER.info('queue closed: %s' % self.__class__.__name__)
                    break
                time.sleep(0)
                continue
            delay = self.delay()
            if delay > 0:
                step.logger.warning('delay %ss' % str(delay))
            time.sleep(delay)
            try:
              doc.set_status(step.name, Status.STARTED)
              next_name, next_arg = step.process(doc, arg)
              doc.set_status(step.name, Status.FINISHED)
            except Exception as e:
                doc.set_status(step.name, Status.ERROR)
                step.logger.warning('exception while processing %s with %s' % (doc, step.name), exc_info=True)
                end_report_step = Step.REGISTRY['end']
                end_report_step.enqueue(doc, None)
                continue
            if next_name is not None:
                next_step = Step.get(next_name)
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


#
# end and report step
#

class EndReportProvider(ConstantDelayProvider):
    def __init__(self):
        ConstantDelayProvider.__init__(self)


class EndReportStep(Step):
    def __init__(self):
        Step.__init__(self, 'end', EndReportProvider)
        outdir = Config.val(Config.OPT_OUTDIR)
        filename = Config.val(Config.OPT_REPORT_FILENAME)
        self.filepath = os.path.join(outdir, filename)
        self.handle = open(self.filepath, 'w')

    def process(self, doc, arg):
        self.handle.write('%s\t%s\t%s\n' % (doc, ', '.join('%s: %s'%i for i in doc.status.items() if i[0] != self.name), arg))
        self.handle.flush()
        with Document.lock:
            Document.count -= 1
        if Document.count == 0:
            Step.close_providers()
        return None, None


#
# check document data steps
#

class CheckDocumentDataProvider(ConstantDelayProvider):
    def __init__(self):
        ConstantDelayProvider.__init__(self)

class CheckDOI(Step):
    def __init__(self, name, with_doi, without_doi):
        Step.__init__(self, name, CheckDocumentDataProvider)
        self.with_doi = with_doi
        self.without_doi = without_doi

    def process(self, doc, arg):
        if doc.doi is None:
            return self.without_doi, None
        return self.with_doi, None









#
# Test
#

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
            Config.LOGGER.warning('%s reset in the past' % self.__class__.__name__)
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
        self.logger.info('redoing: %s (arg is %s; path is %s)' % (doc, arg, doc.status))
        #raise Exception()
        return 'end', None

Config.load('alvis-corpus.rc')
Config.init_logger()
step1 = TestStep1()
step2 = TestStep2()
end_step = EndReportStep()
Step.init_providers()
for i in range(10):
    step1.enqueue(Document())

