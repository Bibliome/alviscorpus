import threading
import queue
import sys
import time
import math
import logging
import os
import os.path
import configparser
import collections
import urllib.parse
import json
import uuid
import enum
import itertools
import requests
import getpass

import alviscorpus.config as config


class Status(enum.Enum):
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
        self.data = collections.defaultdict(dict)
        self.status = collections.OrderedDict()
        with Document.lock:
            Document.count += 1

    def __str__(self):
        if self.doi is None:
            return self.local_id
        return self.doi

    def safe_doi(self):
        if self.doi is None:
            raise Exception()
        return urllib.parse.quote(self.doi, safe='')

    def get_dir(self):
        if self.doi is None:
            raise Exception()
        outdir = config.val(config.SECTION_DOCS, config.OPT_OUTDIR)
        r = os.path.join(outdir, self.safe_doi())
        if not os.path.exists(r):
            os.makedirs(r)
        return r

    def get_filename(self, ext):
        basename = '%s.%s' % (self.safe_doi(), ext)
        return os.path.join(self.get_dir(), basename)
    
    def dump_metadata(self):
        outfile = self.get_filename('md.json')
        with open(outfile, 'w') as f:
            json.dump(self.data, f, indent=2)

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
        self.logger = config.get_logger(name)
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
        self.queue = queue.Queue()
        self.closed = False
        self.lock = threading.Lock()

    def run(self):
        config.logger.info('queue started: %s' % self.__class__.__name__)
        while True:
            try:
                step, doc, arg = self.queue.get_nowait()
            except queue.Empty:
                if self.closed:
                    config.logger.info('queue closed: %s' % self.__class__.__name__)
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
            classes = [type('PoolProvider%02d' % i, (ConstantDelayProvider,), { '__init__': ctor }) for i in range(int(config.val(config.OPT_THREAD_POOL)))]
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
        outdir = config.val(config.OPT_OUTDIR)
        filename = config.val(config.OPT_REPORT_FILENAME)
        self.filepath = os.path.join(outdir, filename)
        self.handle = open(self.filepath, 'w')

    def process(self, doc, arg):
        self.handle.write('%s\t%s\t%s\n' % (doc, ', '.join('%s: %s'%i for i in doc.status.items() if i[0] != self.name), arg))
        self.handle.flush()
        doc.dump_metadata()
        with Document.lock:
            Document.count -= 1
        if Document.count == 0:
            Step.close_providers()
            self.handle.close()
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
    OPT_PROXY = 'proxy'
    
    def __init__(self):
        LimitIntervalProvider.__init__(self, 50, 1)
        config.fill_defaults(CrossRefProvider.SECTION_CROSSREF, {
            CrossRefProvider.OPT_HOST: CrossRefProvider.VAL_HOST
        })

class CrossRefBase(Step):
    _headers = None
    _proxy = None
    
    def __init__(self, name):
        Step.__init__(self, name, CrossRefProvider)

    @staticmethod
    def headers():
        if CrossRefBase._headers is None:
            CrossRefBase._headers = {
                'User-Agent': 'alviscorpus/0.0.1 (https://github.com/Bibliome/alviscorpus; mailto: %s)' % config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_EMAIL),
                'Accept': '*/*',
                'Host': config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_HOST)
            }
        return CrossRefBase._headers

    @staticmethod
    def proxy():
        if CrossRefBase._proxy is None:
            if config.has(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_PROXY):
                proxy_name = config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_PROXY)
                CrossRefBase._proxy = config.proxy(proxy_name)
            else:
                CrossRefBase._proxy = {}
        return CrossRefBase._proxy
                
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
            auth=CrossRefBase.auth,
            proxies=CrossRefBase.proxy()
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
        return 'https://' + config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_HOST) + self.build_url_suffix(doc, arg)

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
            config.logger.warning('%s reset in the past' % self.__class__.__name__)
            return 0
        return int(math.ceil(self.reset - time.time()))

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

config.load('alvis-corpus.rc')
config.init_logger()
cr = CrossRef('crossref', (Step.END, 'ok'), (Step.END, 'cr-no-doi'), (Step.END, 'cr-not-found'))
end_step = EndReportStep()
Step.init_providers()
with open('test-doi.txt') as f:
    for doi in f:
        doc = Document()
        doc.doi = doi.strip()
        cr.enqueue(doc)

