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
import alviscorpus.status as status
import alviscorpus.document as document
import alviscorpus.step as step
import alviscorpus.provider as provider    
import alviscorpus.steplib as steplib
import alviscorpus.crossref as crossref
    

class RemainResetTest(provider.Provider):
    def __init__(self, remain=2, reset=time.time()+2):
        provider.Provider.__init__(self)
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
        
class TestStep1(step.Step):
    def __init__(self):
        step.Step.__init__(self, 'step1', RemainResetTest)

    def process(self, doc, arg):
        self.logger.info('doing: %s' % doc)
        self.provider.set_remain(-1)
        return 'step2', 'foo'

class TestStep2(step.Step):
    def __init__(self):
        step.Step.__init__(self, 'step2')

    def process(self, doc, arg):
        self.logger.info('redoing: %s (arg is %s; path is %s)' % (doc, arg, doc.status))
        #raise Exception()
        return step.END, 'ok'

config.load('alvis-corpus.rc')
config.init_logger()
steplib.EndReportStep(step.END)
cr = crossref.CrossRef('crossref', (step.END, 'ok'), (step.END, 'cr-no-doi'), (step.END, 'cr-not-found'))
step.init_providers()
with open('test-doi.txt') as f:
    for doi in f:
        doc = document.Document()
        doc.doi = doi.strip()
        cr.enqueue(doc)
