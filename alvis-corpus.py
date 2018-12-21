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
import itertools
import requests


class Config(ConfigParser):
    _singleton = None
    LOGGER_ROOT = 'alviscorpus'
    SECTION_GLOBAL = 'global'
    SECTION_LOGGING = 'logging'
    SECTION_DOCS = 'documents'
    OPT_OUTDIR = 'outdir'
    OPT_REPORT_FILENAME = 'report'
    OPT_THREAD_POOL = 'threads'
    MESSAGE_FORMAT = '[%(asctime)s][%(levelname)-8s][%(name)s] %(message)s'
    LOGGER = None
    
    def __init__(self):
        ConfigParser.__init__(self, default_section=Config.SECTION_GLOBAL, interpolation=None)
        self[Config.SECTION_GLOBAL][Config.OPT_OUTDIR] = '.'
        self[Config.SECTION_GLOBAL][Config.OPT_REPORT_FILENAME] = 'report.txt'
        self[Config.SECTION_GLOBAL][Config.OPT_THREAD_POOL] = '4'
        self.add_section(Config.SECTION_LOGGING)
        self.add_section(Config.SECTION_DOCS)

    @staticmethod
    def load(filename):
        return Config._singleton.read(filename)

    @staticmethod
    def _sec_opt(arg1, arg2=None):
        if arg2 is None:
            return Config.SECTION_GLOBAL, arg1
        return arg1, arg2
    
    @staticmethod
    def val(arg1, arg2=None):
        section, opt = Config._sec_opt(arg1, arg2)
        return Config._singleton[section][opt]

    @staticmethod
    def has(arg1, arg2=None):
        section, opt = Config._sec_opt(arg1, arg2)
        return Config._singleton.has_option(section, opt)

    @staticmethod
    def fill_defaults(section, opts):
        if not Config._singleton.has_section(section):
            Config._singleton.add_section(section)
        sec = Config._singleton[section]
        for k, v in opts.items():
            if k not in sec:
                sec[k] = v

    @staticmethod
    def init_logger():
        logger = logging.getLogger(Config.LOGGER_ROOT)
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(logging.Formatter(Config.MESSAGE_FORMAT))
        logger.addHandler(handler)
        Config.LOGGER = Config.get_logger('alvis-corpus')

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
    END = 'end'
    REGISTRY = {}
    
    def __init__(self, name, provider=None):
        if name in Step.REGISTRY:
            raise Exception()
        Step.REGISTRY[name] = self
        self.name = name
        self.logger = Config.get_logger(name)
        self.provider = ProviderPool.get() if provider is None else provider

    def enqueue(self, doc, arg=None):
        self.provider.register(self, doc, arg)
        doc.set_status(self.name, Status.QUEUED)
        
    def process(self, doc, arg=None):
        raise NotImplemented()

    @staticmethod
    def pair(value):
        try:
            a, b = value
            return value
        except TypeError:
            return value, None
            
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


class StepException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        
            
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
                end_report_step = Step.REGISTRY[Step.END]
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


class ProviderPool:
    _instances = None

    @staticmethod
    def _ensure():
        if ProviderPool._instances is None:
            ctor = lambda self: ConstantDelayProvider.__init__(self, 0)
            classes = [type('PoolProvider%02d' % i, (ConstantDelayProvider,), { '__init__': ctor }) for i in range(int(Config.val(Config.OPT_THREAD_POOL)))]
            ProviderPool._instances = itertools.cycle(classes)

    @staticmethod
    def get():
        ProviderPool._ensure()
        return next(ProviderPool._instances)


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

    
#
# end and report step
#


class EndReportStep(Step):
    def __init__(self):
        Step.__init__(self, Step.END)
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
        self.with_doi = Step.pair(with_doi)
        self.without_doi = Step.pair(without_doi)

    def process(self, doc, arg):
        if doc.doi is None:
            return self.without_doi
        return self.with_doi

class CheckMetadata(Step):
    def __init__(self, name, ns, field, with_field, without_field, without_ns):
        Step.__init__(self, name, CheckDocumentDataProvider)
        self.ns = ns
        self.field = field
        self.with_field = Step.pair(with_field)
        self.without_field = Step.pair(without_field)
        self.without_ns = Step.pair(without_ns)

    def process(self, doc, arg):
        if self.ns not in doc.data:
            return self.without_ns
        if self.field is None:
            return self.with_field
        data = doc.data[self.ns]
        if self.field not in data:
            return self.without_field
        return self.with_field

def CheckMetadataNamespace(name, ns, with_ns, without_ns):
    return CheckMetadata(name, ns, None, with_ns, None, without_ns)


#
# CrossRef
#

class CrossRefProvider(LimitIntervalProvider):
    HEADER_LIMIT = 'X-Rate-Limit-Limit'
    HEADER_INTERVAL = 'X-Rate-Limit-Interval'
    SECTION_CROSSREF = 'crossref'
    OPT_HOST = 'host'
    VAL_HOST = 'api.crossref.org'
    OPT_EMAIL = 'email'
    
    def __init__(self):
        LimitIntervalProvider.__init__(self, 50, 1)
        Config.fill_defaults(CrossRefProvider.SECTION_CROSSREF, {
            CrossRefProvider.OPT_HOST: CrossRefProvider.VAL_HOST
        })

class CrossRefBase(Step):
    _headers = None
    
    def __init__(self, name):
        Step.__init__(self, name, CrossRefProvider)

    @staticmethod
    def headers():
        if CrossRefBase._headers is None:
            CrossRefBase._headers = {
                'User-Agent': 'alviscorpus/0.0.1 (https://github.com/Bibliome/alviscorpus; mailto: %s)' % Config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_EMAIL),
                'Accept': '*/*',
                'Host': Config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_HOST)
            }
        return CrossRefBase._headers

    @staticmethod
    def auth(h):
        return h

    @staticmethod
    def update_limit_interval(headers):
        if CrossRefProvider.HEADER_LIMIT in headers and CrossRefProvider.HEADER_INTERVAL in headers:
            CrossRefProvider._singleton.limit = int(headers[CrossRefProvider.HEADER_LIMIT])
            CrossRefProvider._singleton.interval = int(headers[CrossRefProvider.HEADER_INTERVAL][:-1])
    
    def process(self, doc, arg):
        pre = self.pre_process(doc, arg)
        if pre is not None:
            return Step.pair(pre)
        r = requests.get(
            self.build_url(doc, arg),
            headers=CrossRefBase.headers(),
            auth=CrossRefBase.auth
            )
        self.logger.debug('CrossRef request: %s' % r.url)
        self.logger.debug('CrossRef request headers: %s' % r.request.headers)
        if r.status_code == 200:
            next_step = self.handle_200(doc, arg, r.json())
        elif r.status_code == 404:
            next_step = self.handle_404(doc, arg, r.json())
        else:
            self.logger.error(r.text)
            raise StepException('CrossRef server returned status %d' % r.status_code)
        CrossRefBase.update_limit_interval(r.headers)
        return Step.pair(next_step)

    def build_url(self, doc, arg):
        return 'https://' + Config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_HOST) + self.build_url_suffix(doc, arg)

    def pre_process(self, doc, arg):
        raise NotImplemented()
    
    def build_url_suffix(self, doc, arg):
        raise NotImplemented()
    
    def handle_200(self, doc, arg, json):
        raise NotImplemented()

    def handle_404(self, doc, arg, json):
        raise NotImplemented()
        
class CrossRef(CrossRefBase):
    def __init__(self, name, next_step, no_doi_step, not_found_step):
        CrossRefBase.__init__(self, name)
        self.next_step = Step.pair(next_step)
        self.no_doi_step = Step.pair(no_doi_step)
        self.not_found_step = Step.pair(not_found_step)

    def pre_process(self, doc, arg):
        if doc.doi is None:
            return self.no_doi_step
        return None

    def build_url_suffix(self, doc, arg):
        return '/works/' + doc.doi

    def handle_200(self, doc, arg, json):
        doc.data['crossref'] = json
        return self.next_step

    def handle_404(self, doc, arg, json):
        return self.not_found_step

    



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
        Step.__init__(self, 'step2')

    def process(self, doc, arg):
        self.logger.info('redoing: %s (arg is %s; path is %s)' % (doc, arg, doc.status))
        #raise Exception()
        return Step.END, 'ok'

Config.load('alvis-corpus.rc')
Config.init_logger()
cr = CrossRef('crossref', (Step.END, 'ok'), (Step.END, 'cr-no-doi'), (Step.END, 'cr-not-found'))
end_step = EndReportStep()
Step.init_providers()
with open('test-doi.txt') as f:
    for doi in f:
        doc = Document()
        doc.doi = doi.strip()
        cr.enqueue(doc)

